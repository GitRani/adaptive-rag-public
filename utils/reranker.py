from sentence_transformers import CrossEncoder

import torch
import logging


logger = logging.getLogger(__name__)
device = "mps" if torch.backends.mps.is_available() else "cpu"


reranker = CrossEncoder("BAAI/bge-reranker-v2-m3", device=device)

def rerank_search(user_query, keyword_json, vector_json, search_num):
    concat_json = keyword_json + vector_json

    # 검색 간 중복 항목 제거
    concat_json = remove_duplicate_data(concat_json)

    # 나중에 결과를 필터링할 document 데이터 준비
    # 나중에 비교 기준은 file_seq + passage_seq
    documents = [
    {
        "file_seq": data['metadata']['file_seq'],
        "passage_seq": data['metadata']['passage_seq'],
        "text": f"{data['file_name']}: {data['content']} (Pages: {data['page_numbers']})"
    }
    for data in concat_json
    ]
    # rerank에 쓰일 pair 생성
    pairs = [[user_query, doc['text']] for doc in documents]

    # rerank 모델로 스코어 뽑기
    logger.info(f"MPS Available: {torch.backends.mps.is_available()}")
    logger.info(f"MPS Built: {torch.backends.mps.is_built()}")
    scores = generate_rerank(pairs)

    id_to_score = {f"{doc['file_seq']}_{doc['passage_seq']}": float(score) for doc, score in zip(documents, scores)}

    # 기존 스코어는 메타데이터에 넣고 새로운 스코어는 리랭크 점수로 업데이트.
    for data in concat_json:
        data["metadata"]["prev_score"] = data["score"]
        fseq = data["metadata"]["file_seq"]
        pseq = data["metadata"]["passage_seq"]
        data["score"] = id_to_score[f"{fseq}_{pseq}"]

    concat_json.sort(key=lambda x:x['score'], reverse=True)

    return concat_json[:search_num]


def remove_duplicate_data(json_data):
    seen = set()
    new_json_data = []

    for data in json_data:
        field_pair = (data['metadata']['file_seq'], data['metadata']['passage_seq'])
        if field_pair not in seen:
            seen.add(field_pair)
            new_json_data.append(data)

    logger.info(f'======== [Reranker] After Remove Duplicate :: {len(new_json_data)} ========')
    return new_json_data


def generate_rerank(pairs):

    return reranker.predict(pairs)


