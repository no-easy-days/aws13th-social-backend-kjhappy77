# Social Backend API

"클라우드 커뮤니티" 서비스의 백엔드 API 서버를 구현합니다.

지난주에 각자 작성한 **REST API Docs**를 기반으로 실제 동작하는 서버를 개발합니다.

수행 방법에 대한 상세는 노션 페이지 내 과제 제출 페이지 (4주차 과제) 에서 확인해주세요!

> [!IMPORTANT]
> 프로젝트 내에는 종류 불문하고 어떠한 비밀번호도 절대 평문으로 저장하지 마세요!
>
> public repository에 키 잘못올리면 골치아파집니다!
> 
> `.env` 파일은 `.gitignore`에 추가하여 Git에 커밋되지 않도록 하세요!

## 📅 제출

- **제출 마감**: 2026.01.19 수업 시작 전
- **제출 방법**: 본 저장소를 Fork하여 작업 후 본인 github id의 브랜치에 PR 제출 할 것

## 📋 과제 수행 방법

### 1. 리포지토리 Fork하기

본 리포지토리를 **no-easy-days** 조직으로 Fork 해주세요.

#### 터미널에서 gh CLI를 사용하여 Fork하기

```bash
# GitHub CLI로 no-easy-days 조직에 Fork
gh repo fork ej31/aws13th-social-backend --org no-easy-days

# Fork한 리포지토리를 로컬에 클론
gh repo clone no-easy-days/aws13th-social-backend
cd aws13th-social-backend
```

> [!TIP]
> GitHub CLI(`gh`)가 설치되어 있지 않다면, [GitHub CLI 설치 가이드](https://cli.github.com/)를 참고하세요.

### 2. 본인의 브랜치로 PR 올리기

본인의 GitHub ID가 포함된 브랜치로 PR을 제출해주세요.

#### 작업 브랜치 목록

- `developer/eunice.shin54`
- `developer/kjhappy77`
- `developer/0206pdh`
- `developer/unbi53`
- `developer/vocolate17`
- `developer/lee940609`
- `developer/ldj990517`
- `developer/huhsungwoo0609`
- `developer/mins8578`
- `developer/rlaehdrbs90`
- `developer/monghowol`
- `developer/kjsskkh01`
- `developer/seonjeongug2`
- `developer/100psk`
- `developer/youngwoo7804`
- `developer/jmw010314`
- `developer/dong.hee4881`
- `developer/lhj990118`
- `developer/jarvan44`
- `developer/dongq511`
- `developer/jeongmin7397`
- `developer/ywkim0201`
- `developer/ri2eeuntt`

#### PR 제출 절차

```bash
# 1. 본인의 브랜치로 체크아웃
git checkout developer/your-github-id

# 2. 작업 수행 및 커밋
git add .
git commit -m "feat: 구현 내용"

# 3. 원격 저장소에 푸시
git push origin developer/your-github-id

# 4. GitHub CLI로 PR 생성 (또는 GitHub 웹에서 생성)
gh pr create --base main --head developer/your-github-id --title "과제 제출: your-github-id" --body "과제 구현 내용"
```

> [!IMPORTANT]
> - 반드시 **본인의 GitHub ID가 포함된 브랜치**로 PR을 제출해주세요.
> - PR은 `main` 브랜치를 base로 생성해주세요.
