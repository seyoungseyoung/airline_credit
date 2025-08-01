"""
웹 검색 엔진 모듈

항공업계 관련 최신 정보를 웹에서 검색하는 기능
"""

import requests
from bs4 import BeautifulSoup
import time
import random
from typing import List, Dict, Optional
import logging
from urllib.parse import quote_plus
import re

logger = logging.getLogger(__name__)

class SearchEngine:
    """웹 검색 엔진 클래스"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def search_airline_industry(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        항공업계 관련 정보 검색
        
        Args:
            query: 검색 쿼리
            max_results: 최대 결과 수
            
        Returns:
            검색 결과 리스트
        """
        try:
            results = []
            
            # 네이버 뉴스 검색
            try:
                naver_results = self._search_naver_news(query, max_results)
                results.extend(naver_results)
                logger.info(f"네이버 뉴스 검색 결과: {len(naver_results)}개")
            except Exception as e:
                logger.warning(f"네이버 뉴스 검색 실패: {e}")
            
            # 네이버 일반 검색 (백업)
            if len(results) < max_results:
                try:
                    naver_web_results = self._search_naver_web(query, max_results - len(results))
                    results.extend(naver_web_results)
                    logger.info(f"네이버 웹 검색 결과: {len(naver_web_results)}개")
                except Exception as e:
                    logger.warning(f"네이버 웹 검색 실패: {e}")
            
            # 구글 검색 (최종 백업)
            if len(results) < max_results:
                try:
                    google_results = self._search_google(query, max_results - len(results))
                    results.extend(google_results)
                    logger.info(f"구글 검색 결과: {len(google_results)}개")
                except Exception as e:
                    logger.warning(f"구글 검색 실패: {e}")
                
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"검색 중 오류 발생: {e}")
            return []
    
    def _search_naver_news(self, query: str, max_results: int) -> List[Dict]:
        """네이버 뉴스 검색"""
        try:
            # 네이버 뉴스 검색 URL
            search_url = f"https://search.naver.com/search.naver?where=news&query={quote_plus(query)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 뉴스 기사 링크 추출 (다양한 선택자 시도)
            news_items = []
            
            # 1. 기본 뉴스 제목 선택자
            news_items = soup.find_all('a', class_='news_tit')
            
            # 2. 뉴스 링크가 포함된 모든 링크
            if not news_items:
                news_items = soup.find_all('a', href=re.compile(r'news\.naver\.com'))
            
            # 3. 일반적인 링크 제목
            if not news_items:
                news_items = soup.find_all('a', class_='link_tit')
            
            # 4. 제목이 있는 모든 링크
            if not news_items:
                news_items = soup.find_all('a', href=True)
                news_items = [item for item in news_items if item.get_text(strip=True) and len(item.get_text(strip=True)) > 10]
            
            for item in news_items[:max_results]:
                title = item.get_text(strip=True)
                url = item.get('href', '')
                
                if title and url:
                    results.append({
                        'title': title,
                        'url': url,
                        'source': '네이버 뉴스'
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"네이버 뉴스 검색 오류: {e}")
            return []
    
    def _search_naver_web(self, query: str, max_results: int) -> List[Dict]:
        """네이버 일반 웹 검색"""
        try:
            # 네이버 웹 검색 URL
            search_url = f"https://search.naver.com/search.naver?query={quote_plus(query)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 웹 검색 결과 링크 추출 (다양한 선택자 시도)
            web_items = []
            
            # 1. 기본 링크 제목 선택자
            web_items = soup.find_all('a', class_='link_tit')
            
            # 2. 뉴스 링크
            if not web_items:
                web_items = soup.find_all('a', href=re.compile(r'news\.naver\.com'))
            
            # 3. 블로그 링크
            if not web_items:
                web_items = soup.find_all('a', href=re.compile(r'blog\.naver\.com'))
            
            # 4. 제목이 있는 모든 링크
            if not web_items:
                web_items = soup.find_all('a', href=True)
                web_items = [item for item in web_items if item.get_text(strip=True) and len(item.get_text(strip=True)) > 5]
            
            for item in web_items[:max_results]:
                title = item.get_text(strip=True)
                url = item.get('href', '')
                
                if title and url and len(title) > 5:
                    results.append({
                        'title': title,
                        'url': url,
                        'source': '네이버 웹'
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"네이버 웹 검색 오류: {e}")
            return []
    
    def _search_google(self, query: str, max_results: int) -> List[Dict]:
        """구글 검색 (간단한 구현)"""
        try:
            # 구글 검색 URL
            search_url = f"https://www.google.com/search?q={quote_plus(query)}"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 검색 결과 링크 추출
            search_results = soup.find_all('a', href=re.compile(r'^https?://'))
            
            for result in search_results[:max_results]:
                title = result.get_text(strip=True)
                url = result.get('href', '')
                
                if title and url and len(title) > 10:
                    results.append({
                        'title': title,
                        'url': url,
                        'source': '구글 검색'
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"구글 검색 오류: {e}")
            return []
    
    def extract_content(self, url: str) -> Optional[str]:
        """
        URL에서 텍스트 내용 추출
        
        Args:
            url: 추출할 URL
            
        Returns:
            추출된 텍스트 내용
        """
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 불필요한 태그 제거
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()
            
            # 텍스트 추출
            text = soup.get_text()
            
            # 텍스트 정리
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:5000]  # 최대 5000자로 제한
            
        except Exception as e:
            logger.error(f"콘텐츠 추출 오류 ({url}): {e}")
            return None
    
    def search_airline_keywords(self) -> List[str]:
        """항공업계 관련 검색 키워드 반환"""
        return [
            "항공",
            "대한항공",
            "아시아나항공",
            "제주항공",
            "티웨이항공",
            "에어부산",
            "항공사",
            "항공업계",
            "항공기",
            "항공편"
        ] 