# privacy-and-terms

sandcorporation 이 만든 앱들의 개인정보처리방침·이용약관을 GitHub Pages 로 게시한다.

앱 저장소가 비공개라 Pages 를 쓸 수 없어서(비공개 저장소 Pages 는 유료 플랜) 정책 문서만
따로 낸다. 여기 있는 문서는 Play Console 이 **URL 로** 요구하는 것들이다.

## 주소

| 문서 | 주소 |
| --- | --- |
| 목록 | https://sandcorporation.github.io/privacy-and-terms/ |
| 줄기노트 개인정보처리방침 | https://sandcorporation.github.io/privacy-and-terms/julginote/privacy/ |

## 구조

```
index.html                    # 문서 목록
julginote/privacy/index.html  # 줄기노트 개인정보처리방침
```

앱을 더 내면 `<앱>/privacy/index.html` 을 더한다. 의존성 없는 정적 HTML 이라 빌드가 없다 —
main 에 push 하면 Pages 가 그대로 낸다.

## 고칠 때

**내용이 바뀌면 문서 안의 게시일도 함께 고친다.** 방침이 언제 것인지 사람이 알 수 있어야
한다. 줄기노트 방침의 원본 마크다운은 앱 저장소의 `docs/store/privacy-policy.md` 에 있으니
둘을 같이 고친다.
