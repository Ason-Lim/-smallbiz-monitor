import os
import re
import urllib.parse
import pandas as pd
from flask import Flask, render_template, send_file, jsonify, request, Response
import database
from crawler.core_crawler import run_crawler_generator

app = Flask(__name__)

# Initialize the SQLite database on startup
database.init_db()

@app.route('/')
def index():
    # Extract filter arguments
    filters = {
        'sido': request.args.get('sido', '전체'),
        'sigungu': request.args.get('sigungu', '전체'),
        'delivery_type': request.args.get('delivery_type', '전체'),
        'status': request.args.get('status', '전체'),
        'keyword': request.args.get('keyword', '').strip()
    }
    
    # Base query without status filter to calculate accurate overall dashboard KPIs
    base_filters = {
        'sido': filters['sido'],
        'sigungu': filters['sigungu'],
        'delivery_type': filters['delivery_type'],
        'keyword': filters['keyword']
    }
    all_programs = database.get_all_programs(base_filters)
    
    # Calculate complete dashboard statistics
    total_count = len(all_programs)
    active_count = sum(1 for item in all_programs if item['status'] == '모집중')
    closing_soon_count = sum(1 for item in all_programs if item['status'] == '마감임박')
    closed_count = sum(1 for item in all_programs if item['status'] in ('마감완료', '마감'))
    direct_budget_pct = int((sum(1 for item in all_programs if '직접' in item['budget_delivery_type']) / total_count * 100)) if total_count > 0 else 0
    
    # Filter data for display according to status
    if filters['status'] == '전체':
        data = all_programs
    elif filters['status'] == '모집중':
        data = [item for item in all_programs if item['status'] == '모집중']
    elif filters['status'] == '마감임박':
        data = [item for item in all_programs if item['status'] == '마감임박']
    elif filters['status'] in ('마감완료', '마감'):
        data = [item for item in all_programs if item['status'] in ('마감완료', '마감')]
    else:
        data = all_programs
        
    # Get distinct region options for filter dropdowns
    sidos, region_mapping = database.get_distinct_regions()
    
    stats = {
        'total': total_count,
        'active': active_count,
        'closing': closing_soon_count,
        'closed': closed_count,
        'direct_pct': direct_budget_pct
    }
    
    return render_template(
        'index.html',
        active_tab='smallbiz',
        data=data,
        filters=filters,
        sidos=sidos,
        region_mapping=region_mapping,
        stats=stats
    )

@app.route('/b2b_gift')
def b2b_gift():
    # Extract filter arguments
    filters = {
        'institution_type': request.args.get('institution_type', '전체'),
        'status': request.args.get('status', '전체'),
        'keyword': request.args.get('keyword', '').strip()
    }
    
    # Base query without status filter to calculate accurate overall dashboard KPIs
    base_filters = {
        'institution_type': filters['institution_type'],
        'keyword': filters['keyword']
    }
    all_bids = database.get_all_gift_bids(base_filters)
    
    # Calculate complete dashboard statistics (KPIs)
    total_count = len(all_bids)
    active_count = sum(1 for item in all_bids if item['status'] == '입찰중')
    closing_soon_count = sum(1 for item in all_bids if item['status'] == '마감임박')
    closed_count = sum(1 for item in all_bids if item['status'] in ('입찰마감', '마감', '마감완료'))
    public_agency_pct = int((sum(1 for item in all_bids if item['institution_type'] in ('공공기관', '지자체 산하기관')) / total_count * 100)) if total_count > 0 else 0
    
    # Filter data for display according to status
    if filters['status'] == '전체':
        data = all_bids
    elif filters['status'] == '입찰중':
        data = [item for item in all_bids if item['status'] == '입찰중']
    elif filters['status'] == '마감임박':
        data = [item for item in all_bids if item['status'] == '마감임박']
    elif filters['status'] in ('입찰마감', '마감', '과거완료'):
        data = [item for item in all_bids if item['status'] in ('입찰마감', '마감', '마감완료')]
    else:
        data = all_bids
        
    stats = {
        'total': total_count,
        'active': active_count,
        'closing': closing_soon_count,
        'closed': closed_count,
        'public_pct': public_agency_pct
    }
    
    return render_template(
        'index.html',
        active_tab='b2b_gift',
        data=data,
        filters=filters,
        stats=stats
    )

def format_hwpx_text(text):
    if not text:
        return ""
    lines = text.split('\n')
    formatted_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('【') or stripped.startswith('['):
            formatted_lines.append(f'<div class="hwp-section-title">{line}</div>')
        elif any(stripped.startswith(prefix) for prefix in ('1.', '2.', '3.', '4.', '5.', '-', '가.', '나.', '다.', '라.')):
            formatted_lines.append(f'<p style="margin-left: 20px; font-weight: 500;">{line}</p>')
        else:
            formatted_lines.append(f'<p>{line}</p>')
    return '\n'.join(formatted_lines)

@app.route('/notice/<tab>/<doc_id>')
def view_notice(tab, doc_id):
    if tab == 'b2b_gift':
        item = database.get_gift_bid_by_id(doc_id)
    else:
        item = database.get_program_by_id(doc_id)
        
    if not item:
        return "공고를 찾을 수 없습니다.", 404
        
    item['formatted_html'] = format_hwpx_text(item.get('hwpx_parsed_text', ''))
    return render_template('notice_detail.html', item=item, tab=tab)

@app.route('/api/view_hwpx/<doc_id>')
def api_view_hwpx(doc_id):
    tab = request.args.get('tab', 'smallbiz')
    if tab == 'b2b_gift':
        doc_item = database.get_gift_bid_by_id(doc_id)
    else:
        doc_item = database.get_program_by_id(doc_id)
        
    if doc_item:
        return jsonify({"success": True, "html_content": doc_item["hwpx_parsed_text"]})
    return jsonify({"success": False, "message": "파일을 찾을 수 없습니다."}), 404

@app.route('/api/run_crawler')
def api_run_crawler():
    """
    Triggers the crawler and streams log output to the client in real-time.
    """
    tab = request.args.get('tab', 'smallbiz')
    return Response(run_crawler_generator(tab=tab), mimetype='text/event-stream')

@app.route('/download')
def download():
    tab = request.args.get('tab', 'smallbiz')
    
    if tab == 'b2b_gift':
        filters = {
            'institution_type': request.args.get('institution_type', '전체'),
            'status': request.args.get('status', '전체'),
            'keyword': request.args.get('keyword', '').strip()
        }
        data = database.get_all_gift_bids(filters)
        if not data:
            df = pd.DataFrame(columns=[
                '기관명', '공고명', '예산규모', '공고일', '입찰 마감일', '담당부서', '담당자', '연락처', '상태', '원본 링크'
            ])
        else:
            df = pd.DataFrame(data).drop(columns=['hwpx_parsed_text', 'id'])
            # Reorder columns
            cols = ['institution', 'title', 'budget', 'announcement_date', 'deadline', 'department', 'manager', 'contact', 'status', 'link']
            df = df[cols]
            df.columns = [
                '기관명', '공고명', '예산규모', '공고일', '입찰 마감일', '담당부서', '담당자', '연락처', '상태', '원본 링크'
            ]
            
        excel_dir = os.path.join(os.path.dirname(__file__), 'data')
        if not os.path.exists(excel_dir):
            os.makedirs(excel_dir)
            
        file_path = os.path.join(excel_dir, "B2B_기프트_모니터_보고서.xlsx")
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='필터링된_선물입찰')
            
        return send_file(file_path, as_attachment=True, download_name="B2B_기프트_모니터_보고서.xlsx")
    else:
        filters = {
            'sido': request.args.get('sido', '전체'),
            'sigungu': request.args.get('sigungu', '전체'),
            'delivery_type': request.args.get('delivery_type', '전체'),
            'status': request.args.get('status', '전체'),
            'keyword': request.args.get('keyword', '').strip()
        }
        data = database.get_all_programs(filters)
        if not data:
            df = pd.DataFrame(columns=[
                '시/도', '시/군/구', '담당 기관', '사업공고일', '사업명', '사업내용', '사업공고 링크',
                '접수마감일', '예산 규모', '참여 대상', '참여 방법', '예산 집행 구조', '접수 방법', '접수 서류', '담당자 연락처', '상태'
            ])
        else:
            df = pd.DataFrame(data).drop(columns=['hwpx_parsed_text', 'id'])
            cols = ['sido', 'sigungu', 'organization', 'announcement_date', 'title', 'content', 'link', 'deadline', 'budget_size', 'target_audience', 'participation_method', 'budget_delivery_type', 'apply_method', 'documents', 'contact_info', 'status']
            df = df[cols]
            df.columns = [
                '시/도', '시/군/구', '담당 기관', '사업공고일', '사업명', '사업내용', '사업공고 링크',
                '접수마감일', '예산 규모', '참여 대상', '참여 방법', '예산 집행 구조', '접수 방법', '접수 서류', '담당자 연락처', '상태'
            ]
            
        excel_dir = os.path.join(os.path.dirname(__file__), 'data')
        if not os.path.exists(excel_dir):
            os.makedirs(excel_dir)
            
        file_path = os.path.join(excel_dir, "소상공인_지원사업_맞춤식_리포트.xlsx")
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='필터링된_지원사업')
            
        return send_file(file_path, as_attachment=True, download_name="소상공인_지원사업_보고서.xlsx")

@app.route('/download_doc/<doc_id>')
def download_doc(doc_id):
    tab = request.args.get('tab', 'smallbiz')
    if tab == 'b2b_gift':
        doc_item = database.get_gift_bid_by_id(doc_id)
    else:
        doc_item = database.get_program_by_id(doc_id)
        
    if doc_item:
        title = doc_item['title']
        # Clean title for filename
        clean_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()
        text_content = f"=== {doc_item.get('title', '공고문')} ===\n"
        if tab == 'b2b_gift':
            text_content += f"기관명: {doc_item.get('institution')}\n"
            text_content += f"예산규모: {doc_item.get('budget')}\n"
            text_content += f"담당부서: {doc_item.get('department')}\n"
            text_content += f"담당자: {doc_item.get('manager')} ({doc_item.get('contact')})\n"
            text_content += f"공고일자: {doc_item.get('announcement_date')} | 입찰마감일자: {doc_item.get('deadline')}\n\n"
        else:
            text_content += f"담당기관: {doc_item.get('organization')}\n"
            text_content += f"지역: {doc_item.get('sido')} {doc_item.get('sigungu')}\n"
            text_content += f"공고일자: {doc_item.get('announcement_date')} | 접수마감일자: {doc_item.get('deadline')}\n\n"
            
        text_content += "--- 상세 내용 ---\n"
        text_content += doc_item.get('hwpx_parsed_text', '')
        
        # Save temporary file or send from memory
        from io import BytesIO
        mem_file = BytesIO()
        mem_file.write(text_content.encode('utf-8'))
        mem_file.seek(0)
        
        filename = f"[공고문]_{clean_title}.txt"
        encoded_filename = urllib.parse.quote(filename)
        
        return Response(
            mem_file,
            mimetype="text/plain; charset=utf-8",
            headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"}
        )
@app.route('/api/debug_db')
def debug_db():
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM gift_bids LIMIT 1")
        row = cursor.fetchone()
        colnames = [desc[0] for desc in cursor.description]
        return {"status": "success", "columns": colnames, "row": row}
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
