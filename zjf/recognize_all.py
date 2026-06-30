import os
import glob
import easyocr
import cv2
import numpy as np

def correct_char(char):
    corrections = {
        '爽': '乘', '乖': '乘', '帅': '乘', '燹': '乘', '椉': '乘', '脦': '乘', '箫': '乘', '丘': '6', '羌': '乘',
        '力': '加', '口': '加', '如': '加', '咖': '加', '地': '加',
        '咸': '减', '碱': '减', '喊': '减',
        '滁': '除', '涂': '除', '蜍': '除', '訾': '除',
        '竽': '等', '箏': '等', '会': '等',
        '亍': '于', '壬': '于', '予': '于', '子': '于', '爷': '于', '干': '于', '工': '于', '手': '于',
        'O': '0', 'o': '0', 'Q': '0', '蛋': '0', '氮': '0', '@': '0',
        '一': '1', '乙': '1', 'l': '1', 'I': '1', '!': '1',
        'Z': '2', 'z': '2',
        'E': '3', 'e': '3', '孓': '3',
        'A': '4', 'a': '4',
        'S': '5', 's': '5',
        'b': '6', 'G': '6', '/': '6',
        'T': '7', 't': '7',
        'B': '8', 'X': '8',
        'q': '9', 'g': '9',
        '^': '', '_': '', '|': '', '·': '', '#': '', '.': '', ';': '', '+': '', '-': '', '*': '', '%': '',
        '《': '', '》': '', '舌': '', '垂': '', '>': '', '~': '', '名': '',
    }
    return corrections.get(char, char)

def correct_text(text):
    corrected = []
    for c in text:
        corrected.append(correct_char(c))
    
    result = ''.join(corrected)
    result = result.replace('等壬', '等于').replace('等亍', '等于')
    result = result.replace('等予', '等于').replace('等子', '等于')
    result = result.replace('等於', '等于').replace('等于', '等于')
    
    return result

def smart_complete(text):
    keywords = ['加', '减', '乘', '除']
    digits = '0123456789'
    
    for kw in keywords:
        if kw in text:
            parts = text.split(kw)
            if len(parts) == 2:
                left = parts[0].strip()
                right_part = parts[1].strip()
                
                right = right_part.replace('等于', '').replace('等', '').replace('于', '')
                
                if not left and right:
                    candidates = []
                    for num in digits:
                        candidate = num + kw + right + '等于'
                        if len(candidate) <= 7:
                            candidates.append(candidate)
                    if candidates:
                        return candidates
                elif left and not right:
                    candidates = []
                    for num in digits:
                        candidate = left + kw + num + '等于'
                        if len(candidate) <= 7:
                            candidates.append(candidate)
                    if candidates:
                        return candidates
                elif not left and not right and '等于' in text:
                    candidates = []
                    for num1 in digits:
                        for num2 in digits:
                            candidate = num1 + kw + num2 + '等于'
                            candidates.append(candidate)
                    if candidates:
                        return candidates
                elif left and right and '等于' not in text and len(left) == 1 and len(right) == 1:
                    return [left + kw + right + '等于']
                elif len(left) == 1 and right and '等于' not in text:
                    return [left + kw + right + '等于']
                elif len(left) == 1 and right and '等于' in text and len(right) == 1:
                    return [left + kw + right + '等于']
    return [text]

def convert_expression(text):
    mapping = {'加': '+', '减': '-', '乘': '*', '除': '/', '等于': '='}
    result = text
    for chinese, symbol in mapping.items():
        result = result.replace(chinese, symbol)
    return result

def calculate_expression(text):
    expr = convert_expression(text)
    expr = expr.replace('=', '')
    try:
        result = eval(expr)
        return int(result) if result == int(result) else result, expr
    except Exception:
        return None, expr

def recognize_with_multiple_params(image_path, reader):
    all_results = []
    
    for params in [
        {}, {'paragraph': True}, {'mag_ratio': 2}, {'mag_ratio': 3},
        {'low_text': 0.3}, {'mag_ratio': 2, 'low_text': 0.3}, {'mag_ratio': 3, 'low_text': 0.3}
    ]:
        result = reader.readtext(image_path, detail=1, **params)
        for item in result:
            if len(item) == 3:
                bbox, text, confidence = item
                all_results.append((text, confidence))
            elif len(item) == 2:
                text, confidence = item
                all_results.append((text, confidence))
    
    try:
        img = cv2.imread(image_path)
        height, width = img.shape[:2]
        scale = 100 / height if height < 50 else 2
        resized = cv2.resize(img, (int(width*scale), int(height*scale)), interpolation=cv2.INTER_CUBIC)
        temp_path = image_path.replace('.jpg', '_resized.jpg')
        cv2.imwrite(temp_path, resized)
        result = reader.readtext(temp_path, detail=1)
        for item in result:
            if len(item) == 3:
                bbox, text, confidence = item
                all_results.append((text, confidence))
            elif len(item) == 2:
                text, confidence = item
                all_results.append((text, confidence))
        result = reader.readtext(temp_path, detail=1, low_text=0.3)
        for item in result:
            if len(item) == 3:
                bbox, text, confidence = item
                all_results.append((text, confidence))
            elif len(item) == 2:
                text, confidence = item
                all_results.append((text, confidence))
    except:
        pass
    
    candidate_scores = {}
    
    for text, confidence in all_results:
        if isinstance(text, list):
            text = ''.join(str(t) for t in text)
        corrected = correct_text(text)
        completions = smart_complete(corrected)
        for completion in completions:
            expr_result, expr = calculate_expression(completion)
            if expr_result is not None:
                if completion not in candidate_scores:
                    candidate_scores[completion] = {'total_confidence': 0, 'count': 0}
                candidate_scores[completion]['total_confidence'] += confidence
                candidate_scores[completion]['count'] += 1
    
    if candidate_scores:
        scores_with_length = []
        for cand, score_info in candidate_scores.items():
            length_bonus = 10 if len(cand) == 5 else 0
            score = score_info['total_confidence'] + length_bonus
            scores_with_length.append((score, cand))
        scores_with_length.sort(reverse=True)
        best_candidate = scores_with_length[0][1]
        return best_candidate
    
    return ''

def main():
    img_dir = r"E:\KiloAutoTest\zjf\img"
    img_files = sorted(glob.glob(os.path.join(img_dir, "*.jpg")))
    
    print("="*80)
    print(f"开始识别 {len(img_files)} 张图片（优化版 - 多参数+智能选择）")
    print("="*80)
    
    reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
    print("\nEasyOCR模型加载完成!\n")
    
    success_count = 0
    for i, img_path in enumerate(img_files, 1):
        filename = os.path.basename(img_path)
        try:
            corrected = recognize_with_multiple_params(img_path, reader)
            completed = corrected
            
            expr_result = None
            converted = ""
            if completed:
                converted = convert_expression(completed)
                if any(kw in completed for kw in ['加', '减', '乘', '除', '等于']):
                    expr_result, expr = calculate_expression(completed)
            
            status = "✓" if expr_result is not None else "?"
            if expr_result is not None:
                success_count += 1
            
            print(f"{i:2d}. [{status}] {filename}")
            print(f"    识别: '{completed}'")
            if converted:
                print(f"    转换: {converted}")
            if expr_result is not None:
                print(f"    结果: {expr_result}")
            print()
            
        except Exception as e:
            print(f"{i:2d}. [✗] {filename}")
            print(f"    错误: {e}\n")
    
    print("="*80)
    print("识别汇总:")
    print("="*80)
    print(f"\n识别成功率: {success_count}/{len(img_files)} = {success_count/len(img_files)*100:.1f}%")

if __name__ == "__main__":
    main()