import requests
import json
import re
import time
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def get_category_urls():
    """삼성 이탈리아 메인 페이지에서 스마트폰을 제외한 카테고리 URL들을 가져옵니다."""
    # 수단으로 정의된 주요 카테고리 (딕셔너리 형태)
    default_categories = {
        "Audio": "https://www.samsung.com/it/audio-sound/all-audio-sound/",
        "Computers": "https://www.samsung.com/it/computers/all-computers/",
        "TVs": "https://www.samsung.com/it/tvs/all-tvs/",
        "Monitors": "https://www.samsung.com/it/monitors/all-monitors/",
        "Refrigerators": "https://www.samsung.com/it/refrigerators/all-refrigerators/",
        "Washing Machines": "https://www.samsung.com/it/washing-machines/all-washing-machines/",
        "Vacuums": "https://www.samsung.com/it/vacuum-cleaners/all-vacuum-cleaners/",
        "Cooking": "https://www.samsung.com/it/cooking-appliances/all-cooking-appliances/",
        "Dishwashers": "https://www.samsung.com/it/dishwashers/all-dishwashers/",
        "Air Conditioners": "https://www.samsung.com/it/air-conditioners/all-air-conditioners/"
    }
    
    return default_categories

def get_product_links_from_category(url):
    """카테고리 페이지에서 상품 URL과 이름을 수집합니다."""
    links = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # 1. LD+JSON (ItemList) 확인 - 가장 정확한 소스
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                if not script.string: continue
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get("@type") == "ItemList":
                        items = data.get("itemListElement", [])
                        for entry in items:
                            item = entry.get("item", {})
                            name = item.get("name")
                            prod_url = item.get("url")
                            offers = item.get("offers", {})
                            
                            # ItemList에 이미 가격 정보가 있는 경우 저장 (나중에 PDP에서 보완)
                            price = "0"
                            if isinstance(offers, dict):
                                price = offers.get("price", "0")
                            
                            if prod_url:
                                if not prod_url.startswith('https'):
                                    prod_url = "https:" + prod_url if prod_url.startswith('//') else "https://www.samsung.com" + prod_url
                                links.append({
                                    "name": name, 
                                    "url": prod_url,
                                    "cat_price": str(price)
                                })
                except:
                    continue
    except Exception as e:
        print(f"Error harvesting links from {url}: {e}")
    return links

def extract_product_details(pdp_url, display_name):
    """PDP 페이지에서 모델 정보와 재고 상태를 추출합니다."""
    variants = []
    try:
        r = requests.get(pdp_url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            return variants
        
        text = r.text
        soup = BeautifulSoup(text, 'html.parser')
        
        # 1. 디지털 데이터 (모델 코드, 이름)
        model_code = ""
        model_code_match = re.search(r'model_code\s*=\s*\"(.*?)\"', text)
        if model_code_match:
            model_code = model_code_match.group(1).replace(r'\/', '/')
            # 유니코드 하이픈 등 처리 (\u002D -> -) - JSON unescape 느낌으로 처리
            try:
                model_code = bytes(model_code, "utf-8").decode("unicode_escape")
            except:
                model_code = model_code.replace(r'\u002D', '-').replace(r'\u002d', '-')
        else:
            # data-modelcode 속성 확인
            tag = soup.find(attrs={"data-modelcode": True})
            if tag:
                model_code = tag["data-modelcode"]
            elif re.search(r'[A-Z0-9]{5,}/?$', pdp_url.rstrip('/')): # URL에서 추출 시도
                mc_match = re.search(r'([A-Z0-9]{5,})/?$', pdp_url.rstrip('/'))
                if mc_match:
                    model_code = mc_match.group(1).upper()
        
        # 최종 모델코드 정규화
        if model_code:
            model_code = model_code.replace(r'\u002D', '-').replace(r'\u002d', '-')

        # 2. 가격 정보 (globalShopInfo 등 JSON 구조에서 추출)
        tax_price = "0"
        list_price = "0"
        sale_price = "0"
        
        shop_info_match = re.search(r'var\s+globalShopInfo\s*=\s*({.*?});', text, re.DOTALL)
        if shop_info_match:
            try:
                # JSON 내의 실제 줄바꿈을 공백으로 치환하여 파싱 에러 방지
                json_str = shop_info_match.group(1).replace('\n', ' ').replace('\r', ' ')
                shop_data = json.loads(json_str)
                tax_price = str(shop_data.get("taxPrice", "0")).replace(',', '')
                sale_price = str(shop_data.get("promotionPrice", "0")).replace(',', '')
                if sale_price == "0":
                    sale_price = str(shop_data.get("price", "0")).replace(',', '')
                
                # priceDisplay에서 숫자 추출
                pd = shop_data.get("priceDisplay", "")
                if pd:
                    pd_clean = pd.replace('.', '').split(',')[0]
                    pd_numeric = "".join(re.findall(r'\d+', pd_clean))
                    if pd_numeric:
                        list_price = pd_numeric
                
                # savePriceInfo에서 숨겨진 정가 추출 (예: <del>1.899,00 €</del>)
                save_info = shop_data.get("savePriceInfo", "")
                if save_info and "<del>" in save_info:
                    del_match = re.search(r'<del>(.*?)</del>', save_info)
                    if del_match:
                        price_text = del_match.group(1).replace('.', '').split(',')[0]
                        price_numeric = "".join(re.findall(r'\d+', price_text))
                        if price_numeric:
                            list_price = price_numeric
            except:
                pass

        # Error Page Check
        if "page not found" in text.lower() or "common/error" in text:
             # Try to extract model from URL even if page is 404/Error
             if not model_code:
                 mc_match = re.search(r'([A-Z0-9-]{5,})/?$', pdp_url.rstrip('/'))
                 if mc_match: model_code = mc_match.group(1).upper()
             if not model_code: return variants

        # Fallback: 기존 패턴 검색
        if sale_price == "0":
            price_match = re.search(r'\"price\"\s*:\s*\"?([\d.,]+)\"?', text)
            if price_match:
                sale_price = price_match.group(1).replace(',', '').split('.')[0]
        
        if tax_price == "0":
            tax_match = re.search(r'\"taxPrice\"\s*:\s*\"?([\d.,]+)\"?', text)
            if tax_match:
                tax_price = tax_match.group(1).replace(',', '').split('.')[0]

        if list_price == "0": list_price = tax_price if tax_price != "0" else sale_price
        if sale_price == "0": sale_price = list_price
        if tax_price == "0": tax_price = list_price

        # 3. 재고 상태
        in_stock = "Aggiungi al carrello" in text or "In stock" in text
        if not in_stock:
            stock_match = re.search(r'\"stockLevelStatus\"\s*:\s*\"(.*?)\"', text)
            if stock_match:
                in_stock = "instock" in stock_match.group(1).lower()

        if model_code:
            # 최종 정수 변환 및 비우기 로직
            try:
                f_tax = str(int(float(tax_price))) if float(tax_price) > 0 else ""
                f_list = str(int(float(list_price))) if float(list_price) > 0 else ""
                f_sale = str(int(float(sale_price))) if float(sale_price) > 0 else "0"
            except:
                f_tax, f_list, f_sale = "", "", sale_price if sale_price != "0" else "0"
            
            # SalePrice와 동일하거나 정보가 없는 경우 비움 (TaxPrice만 null 처리)
            if f_tax == f_sale: f_tax = ""
            
            variant = {
                "ModelCode": model_code,
                "Name": display_name,
                "Url": pdp_url,
                "TaxPrice": f_tax,
                "ListPrice": f_list,
                "SalePrice": f_sale,
                "InStock": in_stock
            }
            if variant not in variants:
                variants.append(variant)

    except Exception as e:
        print(f"Error extracting details from {pdp_url}: {e}")
        
    return variants
