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
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")
        
        return {
            "cache_created": datetime.now().isoformat(),
            "total_entries": 0,
            "entries": {}
        }
    
    def _save_metadata(self):
        """캐시 메타데이터 저장"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")
    
    def _generate_cache_key(self, corp_code: str, year: int, quarter: int, data_type: str = "financial") -> str:
        """캐시 키 생성"""
        key_string = f"{corp_code}_{year}_{quarter}_{data_type}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """캐시 파일 경로 생성"""
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
    
    def is_cache_valid(self, cache_key: str) -> bool:
        """캐시 유효성 검사"""
        if cache_key not in self.metadata["entries"]:
            return False
        
        entry = self.metadata["entries"][cache_key]
        cached_time = datetime.fromisoformat(entry["cached_at"])
        
        return datetime.now() - cached_time < self.cache_duration
    
    def get_cached_data(self, corp_code: str, year: int, quarter: int, data_type: str = "financial") -> Optional[pd.DataFrame]:
        """캐시된 데이터 조회"""
        cache_key = self._generate_cache_key(corp_code, year, quarter, data_type)
        
        if not self.is_cache_valid(cache_key):
            return None
        
        cache_file = self._get_cache_file_path(cache_key)
        
        if not os.path.exists(cache_file):
            # 메타데이터는 있지만 파일이 없는 경우
            logger.warning(f"Cache metadata exists but file missing: {cache_key}")
            self._remove_cache_entry(cache_key)
            return None
        
        try:
            with open(cache_file, 'rb') as f:
                data = pickle.load(f)
            
            # 액세스 시간 업데이트
            self.metadata["entries"][cache_key]["last_accessed"] = datetime.now().isoformat()
            self._save_metadata()
            
            logger.info(f"📦 Cache hit: {corp_code} {year}Q{quarter} ({data_type})")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load cached data: {e}")
            self._remove_cache_entry(cache_key)
            return None
    
    def cache_data(self, corp_code: str, year: int, quarter: int, data: pd.DataFrame, 
                   data_type: str = "financial", company_name: str = "") -> bool:
        """데이터 캐시 저장"""
        if data is None or data.empty:
            logger.warning(f"Empty data provided for caching: {corp_code} {year}Q{quarter}")
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
                "record_count": len(data)
            }
            
            self.metadata["total_entries"] = len(self.metadata["entries"])
            self._save_metadata()
            
            logger.info(f"💾 Cached: {corp_code} {year}Q{quarter} ({data_type}) - {len(data)} records")
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