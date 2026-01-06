import streamlit as st
from openai import OpenAI
import os

# إعداد الصفحة
st.set_page_config(page_title="محول المحاضرات الصوتية", page_icon="🎙️")

# العنوان
st.title("🎙️ محول المحاضرات الصوتية إلى ملخصات")
st.write("ارفع ملف صوتي وسأحوله إلى نص ثم ألخصه لك")

# الحصول على API Key
api_key = st.secrets.get("OPENAI_API_KEY", "")

if not api_key:
    st.error("❌ المفتاح غير موجود! أضف OPENAI_API_KEY في Secrets")
    st.stop()

# إنشاء عميل OpenAI
client = OpenAI(api_key=api_key)

# رفع الملف الصوتي
audio_file = st.file_uploader("اختر ملف صوتي", type=['mp3', 'mp4', 'wav', 'm4a', 'webm'])

if audio_file:
    st.audio(audio_file)
    
    if st.button("🚀 ابدأ التحويل والتلخيص"):
        
        with st.spinner("⏳ جاري تحويل الصوت إلى نص..."):
            try:
                # حفظ الملف مؤقتاً
                with open("temp_audio.mp3", "wb") as f:
                    f.write(audio_file.getbuffer())
                
                # تحويل الصوت إلى نص باستخدام Whisper API
                with open("temp_audio.mp3", "rb") as audio:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio,
                        language="ar"
                    )
                
                transcription_text = transcript.text
                
                st.success("✅ تم التحويل بنجاح!")
                
                # عرض النص الكامل
                with st.expander("📄 النص الكامل"):
                    st.write(transcription_text)
                
                # التلخيص
                with st.spinner("⏳ جاري إنشاء الملخص..."):
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "أنت مساعد ذكي متخصص في تلخيص المحاضرات بشكل منظم وواضح."},
                            {"role": "user", "content": f"لخص هذه المحاضرة بشكل منظم مع ذكر النقاط الرئيسية:\n\n{transcription_text}"}
                        ]
                    )
                    
                    summary = response.choices[0].message.content
                
                st.success("✅ تم إنشاء الملخص!")
                
                # عرض الملخص
                st.subheader("📝 ملخص المحاضرة")
                st.write(summary)
                
                # زر التحميل
                full_content = f"النص الكامل:\n{'='*50}\n{transcription_text}\n\n{'='*50}\n\nالملخص:\n{'='*50}\n{summary}"
                st.download_button(
                    label="📥 تحميل الملخص",
                    data=full_content,
                    file_name="ملخص_المحاضرة.txt",
                    mime="text/plain"
                )
                
                # حذف الملف المؤقت
                os.remove("temp_audio.mp3")
                
            except Exception as e:
                st.error(f"❌ حدث خطأ: {str(e)}")

# تذييل
st.markdown("---")
st.caption("تم التطوير باستخدام Streamlit و OpenAI")
