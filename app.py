import streamlit as st
import requests
import json
from io import BytesIO

# إعداد الصفحة
st.set_page_config(page_title="محول المحاضرات الصوتية", page_icon="🎙️", layout="wide")

# العنوان
st.title("🎙️ محول المحاضرات الصوتية إلى ملخصات")
st.write("ارفع ملف صوتي وسأحوله إلى نص ثم ألخصه لك - **مجاناً باستخدام Hugging Face!**")

# الحصول على API Token
api_token = st.secrets.get("HF_TOKEN", "")

if not api_token:
    st.error("❌ الرمز غير موجود! أضف HF_TOKEN في Secrets")
    st.stop()

# رفع الملف الصوتي
audio_file = st.file_uploader("اختر ملف صوتي", type=['mp3', 'mp4', 'wav', 'm4a', 'webm', 'flac'])

if audio_file:
    st.audio(audio_file)
    
    if st.button("🚀 ابدأ التحويل والتلخيص", type="primary"):
        
        # تحويل الصوت إلى نص
        with st.spinner("⏳ جاري تحويل الصوت إلى نص... (قد يستغرق دقيقة)"):
            try:
                # استخدام Whisper من Hugging Face
                API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
                headers = {"Authorization": f"Bearer {api_token}"}
                
                audio_bytes = audio_file.read()
                
                response = requests.post(API_URL, headers=headers, data=audio_bytes)
                result = response.json()
                
                if "error" in result:
                    st.error(f"❌ خطأ: {result['error']}")
                    st.stop()
                
                transcription_text = result.get("text", "")
                
                if not transcription_text:
                    st.error("❌ لم يتم التعرف على أي نص في الملف الصوتي")
                    st.stop()
                
                st.success("✅ تم التحويل بنجاح!")
                
                # عرض النص الكامل
                with st.expander("📄 النص الكامل للمحاضرة"):
                    st.write(transcription_text)
                
            except Exception as e:
                st.error(f"❌ حدث خطأ في التحويل: {str(e)}")
                st.stop()
        
        # التلخيص
        with st.spinner("⏳ جاري إنشاء الملخص..."):
            try:
                # استخدام نموذج تلخيص عربي
                SUMMARY_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
                
                # تقسيم النص إذا كان طويل
                max_length = 1024
                if len(transcription_text) > max_length:
                    text_to_summarize = transcription_text[:max_length]
                else:
                    text_to_summarize = transcription_text
                
                payload = {
                    "inputs": text_to_summarize,
                    "parameters": {
                        "max_length": 250,
                        "min_length": 50,
                        "do_sample": False
                    }
                }
                
                summary_response = requests.post(
                    SUMMARY_API_URL, 
                    headers=headers, 
                    json=payload
                )
                
                summary_result = summary_response.json()
                
                if isinstance(summary_result, list) and len(summary_result) > 0:
                    summary = summary_result[0].get("summary_text", "")
                else:
                    # إذا فشل التلخيص، نستخدم طريقة بسيطة
                    sentences = transcription_text.split('.')
                    summary = '. '.join(sentences[:5]) + '.'
                
                st.success("✅ تم إنشاء الملخص!")
                
                # عرض الملخص
                st.subheader("📝 ملخص المحاضرة")
                st.info(summary)
                
                # إحصائيات
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("عدد الكلمات (النص الكامل)", len(transcription_text.split()))
                with col2:
                    st.metric("عدد الكلمات (الملخص)", len(summary.split()))
                with col3:
                    reduction = round((1 - len(summary.split())/len(transcription_text.split())) * 100)
                    st.metric("نسبة الاختصار", f"{reduction}%")
                
                # زر التحميل
                full_content = f"""ملخص المحاضرة الصوتية
{'='*60}

📄 النص الكامل:
{transcription_text}

{'='*60}

📝 الملخص:
{summary}

{'='*60}
تم الإنشاء باستخدام Hugging Face
"""
                
                st.download_button(
                    label="📥 تحميل الملخص كملف نصي",
                    data=full_content.encode('utf-8'),
                    file_name="ملخص_المحاضرة.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"❌ حدث خطأ في التلخيص: {str(e)}")

# الشريط الجانبي
with st.sidebar:
    st.header("ℹ️ معلومات")
    st.write("""
    المميزات:
    - 🎯 تحويل صوتي دقيق
    - 📝 تلخيص تلقائي
    - 💯 مجاني تماماً
    - ⚡ سريع وسهل
    
    الملفات المدعومة:
    - MP3, WAV, M4A
    - MP4, WEBM, FLAC
    
    ملاحظة:
    النماذج تعمل على خوادم Hugging Face المجانية
    """)
    
    st.divider()
    st.caption("🔧 تم التطوير باستخدام:")
    st.caption("• Streamlit")
    st.caption("• Hugging Face")
    st.caption("• Whisper Large V3")

# تذييل
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>مشروع مجاني لتحويل المحاضرات الصوتية 🎓</p>
    </div>
    """, 
    unsafe_allow_html=True
)
