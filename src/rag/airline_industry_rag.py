"""
항공업계 RAG 시스템

검색과 요약을 통합하여 항공업계 최신 정보를 GPT 프롬프트에 반영하는 시스템
"""

import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import yaml

from .search_engine import SearchEngine
from .content_summarizer import ContentSummarizer

logger = logging.getLogger(__name__)

class AirlineIndustryRAG:
    """항공업계 RAG 시스템 클래스"""
    
    def __init__(self, openai_api_key: str, cache_dir: str = "rag_cache"):
        """
        초기화
        
        Args:
            openai_api_key: OpenAI API 키
            cache_dir: 캐시 디렉토리
        """
        self.search_engine = SearchEngine()
        self.summarizer = ContentSummarizer(openai_api_key)
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "airline_industry_cache.json")
        
        # 캐시 디렉토리 생성
        os.makedirs(cache_dir, exist_ok=True)
        
        # 캐시 유효기간 (24시간)
        self.cache_duration = timedelta(hours=24)
        
    def get_airline_industry_context(self, force_update: bool = False) -> Dict:
        """
        항공업계 최신 정보 컨텍스트 반환
        
        Args:
            force_update: 강제 업데이트 여부
            
        Returns:
            항공업계 컨텍스트 정보
        """
        try:
            # 캐시 확인
            if not force_update:
                cached_data = self._load_cache()
                if cached_data and self._is_cache_valid(cached_data):
                    logger.info("캐시된 항공업계 정보 사용")
                    return cached_data
            
            # 새로운 정보 검색 및 요약
            logger.info("항공업계 최신 정보 검색 및 요약 시작")
            context = self._search_and_summarize()
            
            # 캐시 저장
            self._save_cache(context)
            
            return context
            
        except Exception as e:
            logger.error(f"항공업계 컨텍스트 생성 오류: {e}")
            return self._get_fallback_context()
    
    def _search_and_summarize(self) -> Dict:
        """검색 및 요약 수행"""
        try:
            # 검색 키워드
            keywords = self.search_engine.search_airline_keywords()
            logger.info(f"검색 키워드: {keywords[:3]}")
            
            # 검색 결과 수집
            all_results = []
            for keyword in keywords[:3]:  # 상위 3개 키워드만 사용 (안정성 향상)
                try:
                    results = self.search_engine.search_airline_industry(keyword, max_results=2)
                    all_results.extend(results)
                    logger.info(f"키워드 '{keyword}' 검색 결과: {len(results)}개")
                    
                    # 요청 간격 조절
                    import time
                    time.sleep(2)
                except Exception as e:
                    logger.warning(f"키워드 '{keyword}' 검색 실패: {e}")
                    continue
            
            # 중복 제거
            unique_results = self._remove_duplicates(all_results)
            logger.info(f"중복 제거 후 결과: {len(unique_results)}개")
            
            # 콘텐츠 추출
            contents = []
            for result in unique_results[:5]:  # 상위 5개만 처리 (안정성 향상)
                try:
                    content = self.search_engine.extract_content(result['url'])
                    if content and len(content) > 100:  # 최소 길이 확인
                        contents.append({
                            'title': result['title'],
                            'content': content,
                            'url': result['url'],
                            'source': result['source']
                        })
                        logger.info(f"콘텐츠 추출 성공: {result['title'][:30]}...")
                    else:
                        logger.warning(f"콘텐츠 추출 실패 또는 너무 짧음: {result['title']}")
                    
                    # 요청 간격 조절
                    import time
                    time.sleep(3)
                except Exception as e:
                    logger.warning(f"콘텐츠 추출 오류: {e}")
                    continue
            
            logger.info(f"최종 처리된 기사: {len(contents)}개")
            
            # 요약 수행
            if contents:
                summary_data = self.summarizer.summarize_multiple_contents(contents)
            else:
                # 기사가 없으면 기본 정보 사용
                summary_data = {
                    "summary": "현재 항공업계 관련 최신 기사를 찾을 수 없습니다. 기본 시장 정보를 제공합니다.",
                    "key_points": [
                        "항공업계는 코로나19 이후 회복세를 보이고 있습니다",
                        "국제선 수요가 점진적으로 증가하고 있습니다",
                        "유가 변동이 항공사 수익성에 영향을 미치고 있습니다",
                        "친환경 항공기 도입이 업계의 주요 이슈입니다"
                    ],
                    "sources": []
                }
            
            # 컨텍스트 구성
            context = {
                "timestamp": datetime.now().isoformat(),
                "summary": summary_data.get("summary", "항공업계 정보를 찾을 수 없습니다."),
                "key_points": summary_data.get("key_points", []),
                "sources": summary_data.get("sources", []),
                "search_keywords": keywords[:3],
                "articles_processed": len(contents),
                "status": "success" if contents else "no_articles"
            }
            
            return context
            
        except Exception as e:
            logger.error(f"검색 및 요약 오류: {e}")
            return self._get_fallback_context()
    
    def _remove_duplicates(self, results: List[Dict]) -> List[Dict]:
        """중복 결과 제거"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    def _load_cache(self) -> Optional[Dict]:
        """캐시 로드"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"캐시 로드 오류: {e}")
        return None
    
    def _save_cache(self, data: Dict):
        """캐시 저장"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"캐시 저장 오류: {e}")
    
    def _is_cache_valid(self, cached_data: Dict) -> bool:
        """캐시 유효성 검사"""
        try:
            timestamp_str = cached_data.get('timestamp', '')
            if not timestamp_str:
                return False
            
            cached_time = datetime.fromisoformat(timestamp_str)
            current_time = datetime.now()
            
            return (current_time - cached_time) < self.cache_duration
            
        except Exception as e:
            logger.error(f"캐시 유효성 검사 오류: {e}")
            return False
    
    def _get_fallback_context(self) -> Dict:
        """폴백 컨텍스트 반환"""
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": "항공업계 정보 검색 중 오류가 발생했습니다. 기본 정보를 사용합니다.",
            "key_points": [
                "항공업계는 여전히 코로나19 영향에서 회복 중",
                "유가 변동과 환율 리스크가 주요 변수",
                "AI와 디지털화를 통한 운영 효율성 향상 추진",
                "환경 규제 대응을 위한 친환경 기술 투자 확대",
                "글로벌 경기 불확실성으로 인한 수요 변동성 존재"
            ],
            "sources": [],
            "search_keywords": [],
            "articles_processed": 0,
            "status": "fallback"
        }
    
    def get_prompt_context(self) -> str:
        """
        GPT 프롬프트에 사용할 컨텍스트 문자열 반환
        
        Returns:
            프롬프트 컨텍스트 문자열
        """
        context = self.get_airline_industry_context()
        
        prompt_context = f"""
=== 항공업계 최신 동향 (업데이트: {context.get('timestamp', 'N/A')}) ===

{context.get('summary', '정보 없음')}

주요 포인트:
"""
        
        key_points = context.get('key_points', [])
        for i, point in enumerate(key_points, 1):
            prompt_context += f"{i}. {point}\n"
        
        if not key_points:
            prompt_context += "현재 항공업계의 주요 동향 정보를 확인할 수 없습니다.\n"
        
        prompt_context += "\n위 정보를 참고하여 항공업계 기업들의 신용위험을 종합적으로 분석해주세요."
        
        return prompt_context
    
    def get_cache_info(self) -> Dict:
        """캐시 정보 반환"""
        try:
            if os.path.exists(self.cache_file):
                cached_data = self._load_cache()
                if cached_data:
                    return {
                        "cache_exists": True,
                        "cache_valid": self._is_cache_valid(cached_data),
                        "last_update": cached_data.get('timestamp', 'N/A'),
                        "articles_processed": cached_data.get('articles_processed', 0),
                        "status": cached_data.get('status', 'unknown')
                    }
            
            return {
                "cache_exists": False,
                "cache_valid": False,
                "last_update": "N/A",
                "articles_processed": 0,
                "status": "no_cache"
            }
            
        except Exception as e:
            logger.error(f"캐시 정보 조회 오류: {e}")
            return {
                "cache_exists": False,
                "cache_valid": False,
                "last_update": "N/A",
                "articles_processed": 0,
                "status": "error"
            } 