# %%
!pip install -q wikiextractor gdown
# %%
!pip install --upgrade pip
# %%
!pip install pandas
!pip install gdown
!pip install openpyxl

# %%
# 필요 패키지 load
import pandas as pd
from tqdm import tqdm
tqdm.pandas()
# import gutenbergpy.textget
from pprint import pprint
import gdown
from collections import Counter
from itertools import chain
# %%
!brew install wget
# %%
!wget https://dumps.wikimedia.org/kowikisource/20250401/kowikisource-20250401-pages-articles.xml.bz2

# %%
!python -m wikiextractor.WikiExtractor --json ./kowikisource-20250401-pages-articles.xml.bz2 --output extracted
# %%
import html
import os
import json
# Wikiextractor 결과물 폴더
extracted_folder = 'extracted'
# JSON 객체를 담을 리스트
data = []
# 폴더 내 모든 파일 순회
for root, dirs, files in os.walk(extracted_folder):
    for file in files:
        file_path = os.path.join(root, file)

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                try:
                    json_obj = json.loads(line.strip())
                    unescaped_text = html.unescape(json_obj)
                    data.append(unescaped_text)
                except json.JSONDecodeError:
                    pass
# %%
# DataFrame 만들기
df = pd.DataFrame(data)

# 결과 확인
print(df.head())
# %%
def process_getPoemLines(data, author, pre_text, index_number):
    if not data.empty and index_number < len(data):
        title = data.iloc[index_number].get('title', '')
        body = data.iloc[index_number].get('text', '')

        # <poem>과 </poem> 태그 제거
        body_without_tags = body.replace('&lt;poem&gt;', '').replace('&lt;/poem&gt;', '')
        body_lines = body_without_tags.strip().split('\n')
        poem_df = pd.DataFrame({'Line': body_lines, 'Title': [title] * len(body_lines), 'Poet': author})

        if pre_text is not None and not pre_text.empty:
            combined_text = pd.concat([pre_text, poem_df], ignore_index=True)
            return combined_text
        else:
            return poem_df
    else:
        if pre_text is not None:
            return pre_text
        else:
            return pd.DataFrame(columns=['Line', 'Title', 'Poet'])
# %%
def process_getPoemLinesFull(data, author, pre_text, title_to_search):
    combined_text = pre_text.copy()  # 이전 text를 복사하여 유지
    filtered_poems = data[data['title'].str.contains(title_to_search, na=False)]

    if not filtered_poems.empty:
        for index, row in filtered_poems.iterrows():
            title = row.get('title', '')
            body = row.get('text', '')

            # <poem>과 </poem> 태그 제거
            body_without_tags = body.replace('&lt;poem&gt;', '').replace('&lt;/poem&gt;', '')
            body_lines = body_without_tags.strip().split('\n')
            poem_df = pd.DataFrame({'Line': body_lines, 'Title': [title] * len(body_lines), 'Poet': author})
            combined_text = pd.concat([combined_text, poem_df], ignore_index=True)

    return combined_text

# %%
text = pd.DataFrame(columns=['Line', 'Title', 'Poet'])
# %%
# 검색 데이터 확인.
title = '진달래꽃'
author = '김소월'
check = df[df['title'].str.contains(title)]
check
#%%
# 시를 하나씩 가져와서 행을 분절.
text = process_getPoemLines(check, author, text, 1)
# %%
text1 = pd.DataFrame(columns=['Line', 'Title', 'Poet'])
# %%
text1 = process_getPoemLinesFull(df, author, text1, title)
#%%
print(text1.head())
print(f"총 {len(text_full)} 행")
# %%
# 엑셀로 저장하기
text.to_excel('작품_추출_.xlsx')

# %%
text1.to_excel('시집_추출.xlsx')