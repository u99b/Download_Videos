const SERVER = 'http://localhost:7282';

window.onload = () => checkStatus();

async function checkStatus() {
    const status = document.getElementById('status');
    status.className = 'status checking';
    status.textContent = '⏳ جاري التحقق...';
    
    try {
        const res = await fetch(`${SERVER}/health`);
        if (res.ok) {
            const data = await res.json();
            status.className = 'status online';
            status.textContent = '✅ الخادم متصل - ' + data.message;
        } else {
            throw new Error('Server error');
        }
    } catch {
        status.className = 'status offline';
        status.textContent = '❌ الخادم غير متصل. الرجاء تشغيل server.py أولاً';
    }
}

async function download() {
    const url = document.getElementById('url').value.trim();
    const result = document.getElementById('result');
    const btn = document.getElementById('dlBtn');
    
    result.style.display = 'none';

    if (!url) {
        showResult('الرجاء إدخال رابط الفيديو.', 'error');
        return;
    }

    if (url.includes('twitter.com') || url.includes('x.com')) {
        showResult('عذراً، لا يمكننا تحميل مقاطع من تويتر.', 'error');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = 'جاري التحميل <span class="spinner"></span>';

    try {
        showResult('جاري معالجة الرابط...', 'info');
        
        const res = await fetch(`${SERVER}/api/download?url=${encodeURIComponent(url)}`);
        
        if (!res.ok) {
            if (res.status === 404) {
                throw new Error('الخادم غير شغال. الرجاء تشغيل server.py أولاً');
            }
            const err = await res.json();
            throw new Error(err.error || 'تعذّر الوصول لخدمة التحميل.');
        }

        const data = await res.json();
        
        let video = null;
        let audio = null;
        
        if (data.links && Array.isArray(data.links)) {
            for (const link of data.links) {
                const type = (link.type || '').toLowerCase();
                const u = link.url || link.link;
                if (type === 'video' && !video) video = u;
                if (type === 'audio' && !audio) audio = u;
            }
        }
        
        if (!video && data.video) video = data.video;
        if (!audio && data.audio) audio = data.audio;

        if (!video && !audio) {
            throw new Error('لا يوجد وسائط قابلة للتحميل.');
        }

        let html = '<div class="meta-info">';
        if (data.title) html += `<div><strong>📹 العنوان:</strong> ${data.title}</div>`;
        if (data.description) html += `<div><strong>📝 الوصف:</strong> ${data.description}</div>`;
        if (data.hashtags) {
            const tags = Array.isArray(data.hashtags) ? data.hashtags.join(' ') : data.hashtags;
            html += `<div><strong>🏷️ هاشتاكات:</strong> ${tags}</div>`;
        }
        html += '</div><div class="download-links">';
        
        if (video) html += `<a href="#" onclick="directDownload('${video}', 'video'); return false;" class="download-link">📹 تحميل الفيديو</a>`;
        if (audio) html += `<a href="#" onclick="directDownload('${audio}', 'audio'); return false;" class="download-link">🎵 تحميل الصوت</a>`;
        html += '</div>';
        
        showResult(html, 'success');
        checkStatus();
        
    } catch (err) {
        showResult(err.message || 'حدث خطأ في الاتصال.', 'error');
        if (err.message.includes('الخادم غير شغال')) checkStatus();
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'تحميل الفيديو';
    }
}

function directDownload(url, type) {
    try {
        showResult('جاري تحميل الملف...', 'info');
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `${type}_${Date.now()}.mp4`;
        link.target = '_blank';
        link.setAttribute('download', '');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        setTimeout(() => {
            showResult('تم بدء التحميل! ✅', 'success');
        }, 500);
    } catch (err) {
        showResult('حدث خطأ في التحميل. جرب مرة أخرى.', 'error');
    }
}

function showResult(msg, type) {
    const result = document.getElementById('result');
    result.innerHTML = msg;
    result.className = 'result ' + type;
    result.style.display = 'block';
}
