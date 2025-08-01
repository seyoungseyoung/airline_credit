"""
콘텐츠 요약 모듈

검색된 항공업계 정보를 GPT를 사용하여 요약하는 기능
"""

import openai
from typing import List, Dict, Optional
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ContentSummarizer:
    """콘텐츠 요약 클래스"""
    
    def __init__(self, api_key: str):
        """
        초기화
        
        Args:
            api_key: OpenAI API 키
        """
        self.client = openai.OpenAI(api_key=api_key)
        
    def summarize_content(self, content: str, max_length: int = 500) -> Optional[str]:
        """
        콘텐츠 요약
        
        Args:
            content: 요약할 콘텐츠
            max_length: 최대 요약 길이
            
        Returns:
            요약된 텍스트
        """
        try:
            if not content or len(content.strip()) < 50:
                return None
                
            prompt = f"""
다음 항공업계 관련 기사를 핵심만 간결하게 요약해주세요.
요약은 {max_length}자 이내로 작성하고, 항공업계의 경영상황, 리스크, 전망 등에 집중해주세요.

기사 내용:
{content[:3000]}

요약:
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 항공업계 전문 분석가입니다. 기사를 간결하고 정확하게 요약해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            return summary if summary else None
            
        except Exception as e:
            logger.error(f"콘텐츠 요약 오류: {e}")
            return None
    
    def summarize_multiple_contents(self, contents: List[Dict]) -> Dict:
        """
        여러 콘텐츠를 종합 요약
        
        Args:
            contents: 콘텐츠 리스트 (각각 title, content, url 포함)
            
        Returns:
            종합 요약 정보
        """
        try:
            if not contents:
                return {
                    "summary": "최신 항공업계 정보를 찾을 수 없습니다.",
                    "key_points": [],
                    "sources": []
                }
            
            # 개별 요약
            summaries = []
            sources = []
            
            for content in contents:
                if content.get('content'):
                    summary = self.summarize_content(content['content'])
                    if summary:
                        summaries.append({
                            'title': content.get('title', ''),
                            'summary': summary,
                            'url': content.get('url', '')
                        })
                        sources.append(content.get('url', ''))
            
            if not summaries:
                return {
                    "summary": "요약 가능한 항공업계 정보를 찾을 수 없습니다.",
                    "key_points": [],
                    "sources": []
                }
            
            # 종합 요약
            combined_summary = self._create_combined_summary(summaries)
            
            # 핵심 포인트 추출
            key_points = self._extract_key_points(summaries)
            
            return {
                "summary": combined_summary,
                "key_points": key_points,
                "sources": sources,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"종합 요약 오류: {e}")
            return {
                "summary": "요약 중 오류가 발생했습니다.",
                "key_points": [],
                "sources": []
            }
    
    def _create_combined_summary(self, summaries: List[Dict]) -> str:
        """개별 요약들을 종합하여 하나의 요약 생성"""
        try:
            combined_text = "\n\n".join([
                f"제목: {s['title']}\n요약: {s['summary']}"
                for s in summaries
            ])
            
            prompt = f"""
다음 항공업계 관련 기사들의 요약을 종합하여 2025년 현재 항공업계의 전반적인 상황을 
간결하게 정리해주세요. 다음 형식으로 작성해주세요:

1. 현재 항공업계 상황
2. 주요 리스크 요인
3. 향후 전망

기사 요약들:
{combined_text}

종합 요약:
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 항공업계 전문 분석가입니다. 여러 기사를 종합하여 항공업계 현황을 정확하게 분석해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"종합 요약 생성 오류: {e}")
            return "항공업계 정보를 종합 요약할 수 없습니다."
    
    def _extract_key_points(self, summaries: List[Dict]) -> List[str]:
        """핵심 포인트 추출"""
        try:
            combined_text = "\n".join([s['summary'] for s in summaries])
            
            prompt = f"""
다음 항공업계 관련 요약들에서 가장 중요한 핵심 포인트 5개를 추출해주세요.
각 포인트는 한 문장으로 간결하게 작성해주세요.

요약 내용:
{combined_text}

핵심 포인트:
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "항공업계 전문가로서 핵심 포인트를 정확하게 추출해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            key_points_text = response.choices[0].message.content.strip()
            
            # 번호가 있는 리스트 형태로 파싱
            points = []
            for line in key_points_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('•') or line.startswith('-') or line.startswith('*')):
                    # 번호나 불릿 포인트 제거
                    point = line.lstrip('0123456789.•-* ').strip()
                    if point:
                        points.append(point)
            
            return points[:5]  # 최대 5개
            
        except Exception as e:
            logger.error(f"핵심 포인트 추출 오류: {e}")
            return [] 