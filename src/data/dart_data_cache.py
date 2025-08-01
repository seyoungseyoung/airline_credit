#!/usr/bin/env python3
"""
DART 데이터 캐시 시스템
===================

실제 DART API 호출 결과를 캐시하여 중복 수집을 방지하는 시스템

Author: Korean Airlines Credit Rating Analysis
"""

import os
import json
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class DARTDataCache:
    """
    DART API 데이터 캐시 관리 시스템
    """
    
    def __init__(self, cache_dir: str = "dart_cache", cache_duration_hours: int = 24):
        """
        캐시 시스템 초기화
        
        Args:
            cache_dir: 캐시 파일 저장 디렉토리
            cache_duration_hours: 캐시 유효 시간 (시간 단위)
        """
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(hours=cache_duration_hours)
        
        # 캐시 디렉토리 생성
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 메타데이터 파일 경로
        self.metadata_file = os.path.join(self.cache_dir, "cache_metadata.json")
        
        # 메타데이터 로드 또는 초기화
        self.metadata = self._load_metadata()
        
        logger.info(f"✅ DART Cache initialized: {self.cache_dir}")
        logger.info(f"🕐 Cache duration: {cache_duration_hours} hours")
    
    def _load_metadata(self) -> Dict[str, Any]:
        """캐시 메타데이터 로드"""
        logger.info(f"📖 [CACHE] Loading metadata from: {self.metadata_file}")
        
        if os.path.exists(self.metadata_file):
            try:
                logger.info(f"✅ [CACHE] Metadata file exists, loading...")
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                logger.info(f"✅ [CACHE] Metadata loaded successfully: {len(metadata.get('entries', {}))} entries")
                return metadata
            except json.JSONDecodeError as e:
                logger.error(f"❌ [CACHE] JSON decode error loading metadata: {e}")
                logger.error(f"📁 [CACHE] Corrupted metadata file: {self.metadata_file}")
            except Exception as e:
                logger.error(f"❌ [CACHE] Failed to load cache metadata: {e}")
                import traceback
                logger.error(f"❌ [CACHE] Traceback: {traceback.format_exc()}")
        else:
            logger.info(f"📝 [CACHE] Metadata file not found, creating new metadata")
        
        # 새로운 메타데이터 생성
        new_metadata = {
            "cache_created": datetime.now().isoformat(),
            "total_entries": 0,
            "entries": {}
        }
        logger.info(f"✅ [CACHE] Created new metadata")
        return new_metadata
    
    def _save_metadata(self):
        """캐시 메타데이터 저장"""
        try:
            logger.debug(f"💾 [CACHE] Saving metadata to: {self.metadata_file}")
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            logger.debug(f"✅ [CACHE] Metadata saved successfully")
        except Exception as e:
            logger.error(f"❌ [CACHE] Failed to save cache metadata: {e}")
            import traceback
            logger.error(f"❌ [CACHE] Traceback: {traceback.format_exc()}")
    
    def _generate_cache_key(self, corp_code: str, year: int, quarter: int, data_type: str = "financial") -> str:
        """캐시 키 생성"""
        key_string = f"{corp_code}_{year}_{quarter}_{data_type}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """캐시 파일 경로 생성"""
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
    
    def is_cache_valid(self, cache_key: str) -> bool:
        """캐시 유효성 검사"""
        try:
            logger.debug(f"🔍 [CACHE] Checking validity for key: {cache_key}")
            
            if cache_key not in self.metadata["entries"]:
                logger.debug(f"❌ [CACHE] Key not found in metadata: {cache_key}")
                return False
            
            entry = self.metadata["entries"][cache_key]
            cached_time = datetime.fromisoformat(entry["cached_at"])
            current_time = datetime.now()
            age = current_time - cached_time
            
            logger.debug(f"🕐 [CACHE] Cache age: {age}, duration limit: {self.cache_duration}")
            
            is_valid = age < self.cache_duration
            logger.debug(f"{'✅' if is_valid else '❌'} [CACHE] Cache validity: {is_valid}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"❌ [CACHE] Error checking cache validity: {e}")
            return False
    
    def get_cached_data(self, corp_code: str, year: int, quarter: int, data_type: str = "financial") -> Optional[Any]:
        """캐시된 데이터 조회"""
        try:
            logger.info(f"🔍 [CACHE] get_cached_data called: {corp_code} {year}Q{quarter} ({data_type})")
            
            cache_key = self._generate_cache_key(corp_code, year, quarter, data_type)
            logger.info(f"🔑 [CACHE] Generated cache key: {cache_key}")
            
            # 캐시 유효성 검사
            logger.info(f"✅ [CACHE] Checking cache validity for key: {cache_key}")
            if not self.is_cache_valid(cache_key):
                logger.info(f"❌ [CACHE] Cache not valid for key: {cache_key}")
                return None
            
            logger.info(f"✅ [CACHE] Cache is valid for key: {cache_key}")
            
            cache_file = self._get_cache_file_path(cache_key)
            logger.info(f"📁 [CACHE] Cache file path: {cache_file}")
            
            if not os.path.exists(cache_file):
                # 메타데이터는 있지만 파일이 없는 경우
                logger.warning(f"❌ [CACHE] Cache metadata exists but file missing: {cache_key}")
                logger.warning(f"📁 [CACHE] Missing file: {cache_file}")
                self._remove_cache_entry(cache_key)
                return None
            
            logger.info(f"✅ [CACHE] Cache file exists: {cache_file}")
            
            # 파일 크기 확인
            file_size = os.path.getsize(cache_file)
            logger.info(f"📊 [CACHE] Cache file size: {file_size} bytes")
            
            if file_size == 0:
                logger.warning(f"⚠️ [CACHE] Cache file is empty: {cache_file}")
                self._remove_cache_entry(cache_key)
                return None
            
            try:
                logger.info(f"📖 [CACHE] Loading cache file: {cache_file}")
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                
                logger.info(f"✅ [CACHE] Successfully loaded cache data: {type(data)}")
                
                # 액세스 시간 업데이트
                logger.info(f"🕐 [CACHE] Updating access time for key: {cache_key}")
                self.metadata["entries"][cache_key]["last_accessed"] = datetime.now().isoformat()
                self._save_metadata()
                
                logger.info(f"📦 [CACHE] Cache hit: {corp_code} {year}Q{quarter} ({data_type})")
                return data
                
            except pickle.UnpicklingError as e:
                logger.error(f"❌ [CACHE] Pickle unpickling error: {e}")
                logger.error(f"📁 [CACHE] Corrupted cache file: {cache_file}")
                self._remove_cache_entry(cache_key)
                return None
            except EOFError as e:
                logger.error(f"❌ [CACHE] EOF error reading cache file: {e}")
                logger.error(f"📁 [CACHE] Incomplete cache file: {cache_file}")
                self._remove_cache_entry(cache_key)
                return None
            except Exception as e:
                logger.error(f"❌ [CACHE] Failed to load cached data: {e}")
                logger.error(f"📁 [CACHE] Error reading cache file: {cache_file}")
                import traceback
                logger.error(f"❌ [CACHE] Traceback: {traceback.format_exc()}")
                self._remove_cache_entry(cache_key)
                return None
                
        except Exception as e:
            logger.error(f"❌ [CACHE] get_cached_data failed: {e}")
            import traceback
            logger.error(f"❌ [CACHE] Traceback: {traceback.format_exc()}")
            return None
    
    def cache_data(self, corp_code: str, year: int, quarter: int, data: Any, 
                   data_type: str = "financial", company_name: str = "") -> bool:
        """데이터 캐시 저장"""
        if data is None:
            logger.warning(f"Empty data provided for caching: {corp_code} {year}Q{quarter}")
            return False
        
        # DataFrame인 경우에만 empty 체크
        if hasattr(data, 'empty') and data.empty:
            logger.warning(f"Empty DataFrame provided for caching: {corp_code} {year}Q{quarter}")
            return False
        
        cache_key = self._generate_cache_key(corp_code, year, quarter, data_type)
        cache_file = self._get_cache_file_path(cache_key)
        
        try:
            # 데이터 저장
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
            
            # 메타데이터 업데이트
            now = datetime.now().isoformat()
            self.metadata["entries"][cache_key] = {
                "corp_code": corp_code,
                "company_name": company_name,
                "year": year,
                "quarter": quarter,
                "data_type": data_type,
                "cached_at": now,
                "last_accessed": now,
                "file_size": os.path.getsize(cache_file),
                "record_count": len(data) if hasattr(data, '__len__') else 1
            }
            
            self.metadata["total_entries"] = len(self.metadata["entries"])
            self._save_metadata()
            
            record_count = len(data) if hasattr(data, '__len__') else 1
            logger.info(f"💾 Cached: {corp_code} {year}Q{quarter} ({data_type}) - {record_count} records")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cache data: {e}")
            # 실패한 경우 파일 정리
            if os.path.exists(cache_file):
                os.remove(cache_file)
            return False
    
    def _remove_cache_entry(self, cache_key: str):
        """캐시 엔트리 제거"""
        cache_file = self._get_cache_file_path(cache_key)
        
        # 파일 삭제
        if os.path.exists(cache_file):
            os.remove(cache_file)
        
        # 메타데이터에서 제거
        if cache_key in self.metadata["entries"]:
            del self.metadata["entries"][cache_key]
            self.metadata["total_entries"] = len(self.metadata["entries"])
            self._save_metadata()
    
    def invalidate_cache(self, corp_code: str = None, year: int = None, quarter: int = None) -> int:
        """캐시 무효화"""
        removed_count = 0
        keys_to_remove = []
        
        for cache_key, entry in self.metadata["entries"].items():
            should_remove = True
            
            if corp_code and entry["corp_code"] != corp_code:
                should_remove = False
            if year and entry["year"] != year:
                should_remove = False
            if quarter and entry["quarter"] != quarter:
                should_remove = False
            
            if should_remove:
                keys_to_remove.append(cache_key)
        
        for cache_key in keys_to_remove:
            self._remove_cache_entry(cache_key)
            removed_count += 1
        
        if removed_count > 0:
            logger.info(f"🗑️ Invalidated {removed_count} cache entries")
        
        return removed_count
    
    def cleanup_expired_cache(self) -> int:
        """만료된 캐시 정리"""
        removed_count = 0
        keys_to_remove = []
        
        for cache_key, entry in self.metadata["entries"].items():
            cached_time = datetime.fromisoformat(entry["cached_at"])
            if datetime.now() - cached_time >= self.cache_duration:
                keys_to_remove.append(cache_key)
        
        for cache_key in keys_to_remove:
            self._remove_cache_entry(cache_key)
            removed_count += 1
        
        if removed_count > 0:
            logger.info(f"🧹 Cleaned up {removed_count} expired cache entries")
        
        return removed_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 정보"""
        total_size = 0
        valid_entries = 0
        expired_entries = 0
        companies = set()
        
        for cache_key, entry in self.metadata["entries"].items():
            total_size += entry.get("file_size", 0)
            companies.add(entry["company_name"])
            
            if self.is_cache_valid(cache_key):
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            "total_entries": len(self.metadata["entries"]),
            "valid_entries": valid_entries,
            "expired_entries": expired_entries,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "companies_cached": len(companies),
            "cache_duration_hours": self.cache_duration.total_seconds() / 3600,
            "cache_created": self.metadata.get("cache_created", "Unknown")
        }
    
    def list_cached_entries(self, corp_code: str = None) -> List[Dict[str, Any]]:
        """캐시된 엔트리 목록 조회"""
        entries = []
        
        for cache_key, entry in self.metadata["entries"].items():
            if corp_code and entry["corp_code"] != corp_code:
                continue
            
            entry_info = entry.copy()
            entry_info["cache_key"] = cache_key
            entry_info["is_valid"] = self.is_cache_valid(cache_key)
            entry_info["file_exists"] = os.path.exists(self._get_cache_file_path(cache_key))
            
            entries.append(entry_info)
        
        # 최신 순으로 정렬
        entries.sort(key=lambda x: x["cached_at"], reverse=True)
        return entries
    
    def clear_all_cache(self) -> int:
        """모든 캐시 삭제"""
        removed_count = len(self.metadata["entries"])
        
        # 모든 캐시 파일 삭제
        try:
            for cache_key in list(self.metadata["entries"].keys()):
                self._remove_cache_entry(cache_key)
            
            logger.info(f"🗑️ Cleared all cache ({removed_count} entries)")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0


def create_default_cache() -> DARTDataCache:
    """기본 캐시 인스턴스 생성"""
    return DARTDataCache(
        cache_dir="financial_data/dart_cache",
        cache_duration_hours=24  # 24시간 캐시
    )


# 글로벌 캐시 인스턴스 (필요시 사용)
_global_cache = None

def get_global_cache() -> DARTDataCache:
    """글로벌 캐시 인스턴스 반환"""
    global _global_cache
    if _global_cache is None:
        _global_cache = create_default_cache()
    return _global_cache