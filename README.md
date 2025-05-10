# Kişisel Portfolyo ve Blog Sitesi

Modern ve şık bir tasarıma sahip, Flask ile geliştirilmiş kişisel portfolyo ve blog sitesi.

## Özellikler

- 🎨 Modern ve responsive tasarım
- 📱 Mobil uyumlu arayüz
- 📝 Proje ve araştırma yönetimi
- 🔍 Kategori bazlı filtreleme
- 📸 Proje görselleri desteği
- 📝 Markdown desteği ile zengin içerik
- 🔒 Admin paneli
- 🎯 SEO dostu yapı

## Kurulum

1. Projeyi klonlayın:
```bash
git clone https://github.com/kullaniciadi/portfolio-blog.git
cd portfolio-blog
```

2. Sanal ortam oluşturun ve aktifleştirin:
```bash
python -m venv venv
# Windows için:
venv\Scripts\activate
# Linux/Mac için:
source venv/bin/activate
```

3. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

4. `.env` dosyası oluşturun:
```env
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///site.db
```

5. Veritabanını oluşturun:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Uygulamayı çalıştırın:
```bash
flask run
```

## Kullanım

1. Admin paneline giriş yapın (`/admin`)
2. Projeler ve araştırmalar ekleyin
3. Kategorileri ve etiketleri düzenleyin
4. Görselleri yükleyin

## Teknolojiler

- Flask
- SQLAlchemy
- HTML5/CSS3
- JavaScript
- Bootstrap
- Markdown

## Katkıda Bulunma

1. Fork'layın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın. 