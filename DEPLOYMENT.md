# Study Hub Deployment Guide

## GitHub Pages дээр deploy хийх

### 1. GitHub дээр шинэ repository үүсгэх
1. GitHub дээр зочлоход `New repository` дарах
2. Repository нэр: `study-hub`
3. Description: `Монголын шилдэг суралцахуйн платформ`
4. Public сонгох
5. `Create repository` дарах

### 2. Локал файлуудыг GitHub-д push хийх
```bash
cd study-hub-standalone
git init
git add .
git commit -m "Анхны commit: Study Hub платформ"
git branch -M main
git remote add origin https://github.com/[таны-username]/study-hub.git
git push -u origin main
```

### 3. GitHub Pages идэвхжүүлэх
1. Repository дээр `Settings` дээр дарах
2. Зүүн цэсээс `Pages` сонгох
3. Source хэсэгт `Deploy from a branch` сонгох
4. Branch: `main` сонгох
5. Folder: `/ (root)` хэвээр үлдээх  
6. `Save` дарах

### 4. Domain хандах
5-10 минутын дараа:
```
https://[таны-username].github.io/study-hub/
```

## Netlify дээр deploy хийх (өөр сонголт)

### 1. Netlify дээр бүртгүүлэх
- https://netlify.com дээр зочлох
- GitHub акаунтаар нэвтрэх

### 2. Deploy хийх
1. `New site from Git` дарах
2. GitHub repository сонгох
3. Build settings:
   - Build command: (хоосон үлдээх)
   - Publish directory: (хоосон эсвэл `.`)
4. `Deploy site` дарах

### 3. Custom domain (сонголттой)
- Domain Settings дээр custom domain нэмж болно

## Vercel дээр deploy хийх

```bash
npm i -g vercel
vercel
```

Дараа нь зааварын дагуу deployment хийнэ.

## SEO Optimization

GitHub Pages идэвхжүүлсний дараа:

1. **Google Search Console** дээр site нэмэх
2. **Sitemap** submit хийх: `sitemap.xml`
3. **Google Analytics** нэмэх (хэрэгтэй бол)

---
**🚀 Амжилттай deployment!**