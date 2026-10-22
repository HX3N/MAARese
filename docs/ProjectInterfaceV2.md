# 3.3 Project Interface V2 프로토콜

> 원문: [MaaFramework v5.14.3 docs/zh_cn/3.3-ProjectInterfaceV2协议.md](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/3.3-ProjectInterfaceV2协议.md)

> 주의: 이 문서는 `ProjectInterface`의 작성과 사용에 관한 문서이다.
>
> 본문에서는 PI가 `ProjectInterface`를, Client가 PI를 처리할 수 있는 도구를 가리킨다.

## 소개

`ProjectInterface`란 MaaFramework의 표준화된 프로젝트 구조 선언으로, 이 선언은 현재 `interface.json` 파일 하나로 이루어져 있다. PI를 정의하면 MaaFramework의 다양한 파생 도구를 사용할 수 있다. 따라서 범용 프로그래밍 언어만으로 통합할 생각이더라도 기본 정보를 담은 PI를 정의할 것을 권장한다.

> [!TIP]
>
> [커뮤니티 프로젝트](https://github.com/MaaXYZ/MaaFramework#%E7%A4%BE%E5%8C%BA%E9%A1%B9%E7%9B%AE)에서 PI를 사용하는 범용 UI와 기타 도구를 찾아볼 수 있다.

### 버전 설명

업무 진행이 빠르게 반복되어 MaaFramework의 릴리스 주기와 PI의 반복 주기를 잘 맞출 수 없다. 따라서 PI는 별도로 버전을 관리하며, PI의 버전 번호는 MaaFramework release 버전 번호와 완전히 동기화되지 않는다.

독립 버전으로 분리한 시점(2026-1-30)의 버전 번호를 `v2.1.0`으로 정했으며, 이후의 추가 및 수정 사항은 문서에 버전 번호를 표기한다.

| 날짜 | 버전 | 변경 내용 |
| ---- | ---- | -------- |
| 2026-1-30 | v2.1.0 | 독립 버전 릴리스 |
| 2026-1-30 | v2.2.0 | `attach_resource_path` 및 `import` 필드 추가 |
| 2026-2-23 | v2.3.0 | `checkbox` 다중 선택 유형, `option.controller`, `option.resource`, 전역/resource/controller 수준 option, `focus.display` 표시 채널 태그, `preset` 프리셋 구성 필드 추가, `import`에서 `preset` 가져오기 지원 |
| 2026-3-5 | v2.3.1 | option 적용성 필터링 규칙 명확화 |
| 2026-3-9 | v2.4.0 | 최상위 `group` 그룹 선언 및 `task.group` 작업 그룹 필드 추가 |
| 2026-3-23 | v2.5.0 | Client가 Agent 자식 프로세스를 시작할 때 `PI_*` 환경 변수를 주입하도록 규정하여, UI / Client 속성과 현재 선택된 컨트롤러 및 리소스(i18n 해석 완료)를 전달 |
| 2026-4-18 | v2.6.0 | `resource.hash` 리소스 무결성 검증 필드 추가 |
| 2026-5-6 | v2.7.0 | Controller 시작 전에 사용자 정의 프로그램을 실행하기 위한 `pretask` 필드 추가, option 값을 마지막 인자로 전달하는 기능 지원 |
| 2026-6-30 | v2.8.0 | `setting` 작업 설정 페이지 UI 선언 필드 추가; `import`에서 `global_option` 및 `setting` 필드 가져오기 지원; `hotkey` 구성 항목 유형 추가 |
| 2026-7-1 | v2.8.1 | `pretask`에서 `controller` / `resource` 필터 필드 지원, `task.controller` / `task.resource`와 의미가 동일 |
| 2026-7-22 | v2.9.0 | `telemetry` 익명 원격 측정(데이터 계측) 구성 필드 추가 |
| 2026-8-5 | v2.9.1 | `focus` 메시지 템플릿 객체에 `trace` 필드 추가, 콜백 메시지 유형별로 원격 측정에서 노드 결과를 업로드할지 제어하는 데 사용 |
| 2026-8-23 | v2.9.2 | `telemetry.sentry.failure_attachments_sample_rate` 실패 진단 첨부 파일 독립 샘플링 비율 필드 추가 |
| 2026-8-24 | v2.10.0 | `input` 유형 옵션의 `inputs[]`에 `password` 필드 추가, 비밀번호/키 입력을 표시하는 데 사용 |
| 2026-9-6 | v2.10.1 | `checkbox` 유형에 `min_count` / `max_count` 필드 추가, 최소 / 최대 선택 개수 제한에 사용 |
| 2026-9-8 | v2.10.2 | `welcome`에서 문자열 배열 지원 |

## `interface.json`

> [!TIP]
>
> 이 파일은 [schema](https://github.com/MaaXYZ/MaaFramework/blob/main/tools/interface.schema.json) 파일을 통해 힌트와 검증 기능을 얻을 수 있다.
>
> VSCode로 프로젝트 템플릿 폴더를 열면 schema와 파일이 자동으로 연결된다.
>
> `import`로 가져오는 PI 조각 파일은 [interface_import.schema.json](https://github.com/MaaXYZ/MaaFramework/blob/main/tools/interface_import.schema.json)을 통해 힌트와 검증 기능을 얻을 수 있다.
>
### 전체 구조

- interface_version `number`  
  인터페이스 버전 번호. 현재는 2이며, 고정값이고 반드시 설정해야 한다. `interface.json`의 **JSON 구조 메이저 버전**을 식별하는 데 사용된다. PI 문서에는 별도의 독립적인 시맨틱 버전(예: v2.5.0의 환경 변수 규정)이 있으며, 둘이 일대일로 대응할 필요는 없다.

- languages `object`  
  다국어 지원 구성. 키는 언어 코드, 값은 해당 번역 파일 경로이다. 지정하지 않으면 기본적으로 중국어만 지원한다.  
  파일의 상대 경로는 interface.json과 같은 디렉터리를 기준으로 한다.
  
  ```jsonc
  "languages": {
      "zh_cn": "interface_zh.json",
      "en_us": "interface_en.json"
  }
  ```

- name `string`  
  프로젝트 고유 식별자. 프로젝트 ID로 사용된다.

- label `string`  
  프로젝트 표시 이름. 사용자 인터페이스에 표시하는 데 사용된다. 국제화 문자열(`$`로 시작)을 지원한다. 설정하지 않으면 `name` 필드의 값을 표시한다. 선택 사항.

  ```jsonc
  {
    "name": "MyProject", 
    "label": "$project_name"  // 국제화 프로젝트 이름
  }
  ```

- title `string`  
  창 제목. Client는 이 내용을 다른 장식 없이 그대로 표시한다. 선택 사항이며, 기본값은 `name`과 `version`을 이어 붙여 생성한다. 국제화(`$`로 시작)를 지원한다.

- icon `string`  
  애플리케이션 아이콘 파일 경로. 프로젝트 루트 디렉터리 기준 상대 경로이다. 지정하지 않으면 기본 아이콘을 사용한다. 국제화(`$`로 시작)를 지원한다.

- mirrorchyan_rid `string`  
  MirrorChyan 리소스 패키지 식별자. 리소스 관리와 배포에 사용된다.

- mirrorchyan_multiplatform `boolean`  
  멀티 플랫폼 지원 여부. 리소스 패키지의 패키징 및 배포 전략에 영향을 준다.

- github `string`  
  프로젝트 GitHub 저장소 주소. 버전 업데이트 확인과 문제 피드백에 사용된다.  
  **소프트웨어 업데이트 규정:**  
  ~~버전 이력에서 뼈저린 교훈을 얻었기에,~~ 범용 UI는 해당 github release에 대한 업데이트 기능만 제공하고, UI 본체 / MaaFW를 별도로 업데이트하는 기능은 제공하지 않기를 바란다.  
  리소스 작성자가 릴리스할 때 자신이 지정한 UI / MaaFW를 직접 패키징함으로써, 사용자 측에서 리소스 버전이 하나의 UI 및 MaaFW 버전에 유일하게 대응하도록 하여 버전 혼용으로 인한 각종 문제를 피한다.

- version `string`  
  프로젝트 버전 번호. Client가 사용자에게 표시할 수 있으며, 버전 업데이트 확인에도 사용된다.

- contact `string`  
  연락처 정보. "정보" 페이지에 표시된다. 파일 경로, URL 또는 직접 입력한 텍스트를 지원하며, 내용은 Markdown 형식을 지원한다. 국제화(`$`로 시작)를 지원한다.

- license `string`  
  프로젝트 라이선스 정보. "정보" 페이지에 표시된다. 파일 경로, URL 또는 직접 입력한 텍스트를 지원하며, 내용은 Markdown 형식을 지원한다. 국제화(`$`로 시작)를 지원한다.

- welcome `string | string[]` **💡 v2.10.2**  
  환영 메시지. 사용자가 처음 사용할 때 팝업으로 표시되며, 공지로도 사용할 수 있다. 각 문자열은 파일 경로, URL 또는 직접 입력한 텍스트를 지원하고, 내용은 Markdown 형식을 지원하며, 국제화(`$`로 시작)를 지원한다. 공지 제목은 Markdown 내용 안에 작성해야 한다.  
  v2.10.2부터 문자열 배열로 여러 공지를 선언할 수 있으며, Client는 배열 순서대로 표시해야 한다. 배열은 비어 있을 수 없다.  

  ```jsonc
  "welcome": [
      "$notice",
      "announcements/2026/update.md"
  ]
  ```

  Client는 순서가 있는 전체 공지 목록을 기록해야 한다. 공지의 추가, 삭제, 순서 변경 및 임의 내용의 업데이트는 모두 내용 업데이트로 간주하며, 사용자에게 다시 알려야 한다. 구버전 Client는 배열 표기를 해석하지 못할 수 있으므로, 구버전 Client와의 호환이 필요하면 계속 단일 문자열 표기를 사용한다.

- description `string`  
  프로젝트 설명 정보. "정보" 페이지에 표시된다. 파일 경로, URL 또는 직접 입력한 텍스트를 지원하며, 내용은 Markdown 형식을 지원한다. 국제화(`$`로 시작)를 지원한다.

- telemetry `object` **💡 v2.9.0**  
  익명 원격 측정(데이터 계측) 구성. 리소스 작성자 자신의 원격 측정 플랫폼에 크래시와 작업 실행 통계를 보고하는 데 사용된다. 모든 Client가 지원하는 것은 아니다. 선택 사항이며, 구성하지 않으면 어떠한 원격 측정도 수행하지 않는다. 이 필드는 원격 측정 구성의 통합 컨테이너로서 현재는 `sentry` 하위 필드를 제공하며, 향후 다른 플랫폼으로 확장할 수 있다.

  데이터 귀속 및 개인정보 규정:  
  - 원격 측정 구성은 리소스 작성자 자신의 플랫폼 프로젝트를 가리키므로 데이터가 자연스럽게 프로젝트별로 분리된다. 소프트웨어마다 다른 구성을 사용하면 구분할 수 있다. 여러 소프트웨어가 같은 구성을 공유하는 경우, Client는 `release` / tag(예: 프로젝트 이름, `version`)를 통해 같은 프로젝트 안에서 구분해야 한다.  
  - Client는 사용자 승인을 우선해야 한다. 이 필드가 구성되어 있더라도 보고 여부는 Client의 사용자 스위치가 결정한다(기본적으로 켜고 언제든 끌 수 있게 하며, 디버그 / 개발 버전에서는 강제로 비활성화할 것을 권장한다).  

  - sentry `object`  
    [Sentry](https://sentry.io) 기반 원격 측정 구성.

    - dsn `string`  
      Sentry 프로젝트의 DSN. 필수이며, 생략하거나 빈 문자열이면 Sentry 원격 측정을 활성화하지 않는다.

    - tracing `boolean`  
      성능 / 트랜잭션 보고 활성화 여부(작업 시작, 종료 및 각 하위 작업 결과를 트랜잭션 / Span 형태로 보고). 선택 사항이며 기본값은 `true`이다. 끄면 크래시 / 오류만 보고하고 작업 생명주기는 보고하지 않는다.

    - traces_sample_rate `number`  
      트랜잭션 샘플링 비율. 값은 `0`~`1`이다. 선택 사항이며 기본값은 `1.0`이다. 작업은 빈도가 낮은 업무 이벤트이므로 전량 보고하면 정확한 성공 / 실패 통계를 얻을 수 있다. 사용자 수가 많을 때는 Sentry 할당량을 제어하기 위해 낮출 수 있으나, 이 경우 통계는 샘플링 기반이 된다.

    - failure_attachments_sample_rate `number` **💡 v2.9.2**  
      실패 진단 첨부 파일의 독립 샘플링 비율. 값은 `0`~`1`이다. 선택 사항이며 기본값은 `1.0`이다. `0`은 첨부 파일을 업로드하지 않음을, `1`은 조건에 맞는 모든 첨부 파일을 업로드함을 의미한다. 실패 / 오류 이벤트와 함께 업로드되는 첨부 파일만 제어하며, 해당 Error Event, Sentry Logs 또는 트랜잭션 샘플링에는 영향을 주지 않는다. Client가 실패 진단 첨부 파일 수집을 지원하지 않으면 이 필드를 무시할 수 있다.

    - environment `string`  
      환경 태그(예: `production`, `beta`). Sentry에서 구분하는 데 사용된다. 선택 사항이며, 생략하면 Client가 결정한다(예: 업데이트 채널을 사용하거나 `production`으로 대체).

- controller `object[]`  
  컨트롤러 구성. 미리 정의된 컨트롤러 정보를 담은 객체 배열이다.

  - name `string`  
    고유 이름 식별자. 컨트롤러 ID로 사용된다.

  - label `string`  
    표시 이름. 사용자 인터페이스에 표시하는 데 사용된다. 국제화 문자열(`$`로 시작)을 지원한다. 설정하지 않으면 `name` 필드의 값을 표시한다.

  - description `string`  
    컨트롤러 상세 설명 정보. 파일 경로, URL 또는 직접 입력한 텍스트를 지원하며, 내용은 Markdown 형식을 지원한다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

  - icon `string`  
    컨트롤러 아이콘 파일 경로. 프로젝트 루트 디렉터리 기준 상대 경로이다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

  - type `'Adb' | 'Win32' | 'MacOS' | 'PlayCover' | 'Gamepad' | 'Linux'`  
    컨트롤러 유형. 값은 `Adb`, `Win32`(Windows 전용), `MacOS`(macOS 전용), `PlayCover`(macOS 전용), `Gamepad`(Windows 전용), `Linux`
    (Linux 전용)이다.

  - display_short_side `number`  
    기본 스케일링 해상도의 짧은 변 길이. 화면 적응에 사용된다. 선택 사항이며 기본값은 720이다. `display_long_side`, `display_expand`, `display_raw`와 상호 배타적이다.

  - display_long_side `number`  
    기본 스케일링 해상도의 긴 변 길이. 화면 적응에 사용된다. 선택 사항. `display_short_side`, `display_expand`, `display_raw`와 상호 배타적이다.

  - display_expand `[number, number]`  
    Unity Canvas Scaler의 Expand 의미를 따르는 기준 해상도 `[width, height]`: `scale = max(width / raw_width, height / raw_height)`. 원본의 가로세로 비율을 유지하며, 출력의 양변이 모두 기준 해상도 이상이 된다. 선택 사항. `display_short_side`, `display_long_side`, `display_raw`와 상호 배타적이다.

  - display_raw `boolean`  
    스케일링 없이 원본 해상도로 스크린샷을 찍을지 여부. 선택 사항이며 기본값은 false이다. 스케일링 해상도 설정과 상호 배타적이다.

  - permission_required `boolean`  
    이 컨트롤러를 관리자 권한으로 실행해야 하는지 여부. 선택 사항이며 기본값은 false이다.  
    작업을 실행하기 전에 현재 프로세스가 관리자 권한이 아니면 안내를 표시하고 관리자 권한으로 재시작을 시도한다.

  - attach_resource_path `string[]` **💡 v2.2.0**  
    선택 사항. 추가 리소스 경로 배열. `resource.path` 로드가 끝난 뒤, 이 경로들의 리소스를 추가로 로드한다.

  - option `string[]` **💡 v2.3.0**  
    선택 사항. 컨트롤러 수준의 옵션 구성. 문자열 배열이며, 배열 요소는 바깥쪽 option 구성의 키 이름과 대응해야 한다.  
    이 옵션이 생성하는 매개변수는 해당 컨트롤러를 사용하는 모든 작업의 pipeline override에 참여하여 컨트롤러 수준의 매개변수 전달 역할을 한다.  
    참조된 option이 현재 controller/resource 조건을 지원하지 않으면, 해당 option의 `pipeline_override`(중첩된 `option.option` 포함)는 병합에 참여하지 않는다. **💡 v2.3.1**

  - adb `object`  
    `Adb` 컨트롤러의 상세 구성.  

    > **주의:** V2 프로토콜에서 Adb 컨트롤러의 input/screencap은 MaaFramework가 최적의 방식을 자동으로 감지하고 선택하므로 수동으로 구성할 필요가 없다.

  - win32 `object`  
    `Win32` 컨트롤러의 상세 구성.

    - class_regex `string`  
      선택 사항. `Win32` 컨트롤러가 창 클래스 이름을 검색할 때 사용하는 정규 표현식.

    - window_regex `string`  
      선택 사항. `Win32` 컨트롤러가 창 제목을 검색할 때 사용하는 정규 표현식.

    - mouse `string`  
      선택 사항. `Win32` 컨트롤러의 마우스 제어 방식. 제공하지 않으면 기본값을 사용한다. 자세한 내용은 [제어 방식 설명](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/2.4-控制方式说明.md#win32-input)을 참고한다.

    - keyboard `string`  
      선택 사항. `Win32` 컨트롤러의 키보드 제어 방식. 제공하지 않으면 기본값을 사용한다. 자세한 내용은 [제어 방식 설명](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/2.4-控制方式说明.md#win32-input)을 참고한다.

    - screencap `string`  
      선택 사항. `Win32` 컨트롤러의 스크린샷 방식. 제공하지 않으면 기본값을 사용한다. 자세한 내용은 [제어 방식 설명](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/2.4-控制方式说明.md#win32-screencap)을 참고한다.

  - macos `object`  
    `MacOS` 컨트롤러의 상세 구성.

    - title_regex `string`  
      선택 사항. `MacOS` 컨트롤러가 창 제목을 검색할 때 사용하는 정규 표현식.

    - screencap `string`  
      선택 사항. `MacOS` 컨트롤러의 스크린샷 방식. 제공하지 않으면 기본값을 사용한다. 자세한 내용은 [제어 방식 설명](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/2.4-控制方式说明.md#macos-screencap)을 참고한다.

    - input `string`  
      선택 사항. `MacOS` 컨트롤러의 입력 방식. 제공하지 않으면 기본값을 사용한다. 자세한 내용은 [제어 방식 설명](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/2.4-控制方式说明.md#macos-input)을 참고한다.

  - playcover `object`  
    `PlayCover` 컨트롤러의 상세 구성(macOS 전용). PlayCover를 통해 실행되는 iOS 앱을 제어하는 데 사용된다. 자세한 내용은 [제어 방식 설명](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/2.4-控制方式说明.md#playcover-macos)을 참고한다.

    - uuid `string`  
      선택 사항. 대상 앱의 Bundle Identifier. 제공하지 않으면 기본값 `maa.playcover`를 사용하며, 컨트롤러 식별자로만 쓰이고 제어 대상 앱과는 무관하다.

  - gamepad `object`  
    `Gamepad` 컨트롤러의 상세 구성(Windows 전용). 가상 게임패드를 만들어 게임을 제어하는 데 사용된다. [ViGEm Bus Driver](https://github.com/ViGEm/ViGEmBus) 설치가 필요하다. 자세한 내용은 [제어 방식 설명](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/2.4-控制方式说明.md#gamepad-windows)을 참고한다.

    - class_regex `string`  
      선택 사항. `Win32` 컨트롤러가 창 클래스 이름을 검색할 때 사용하는 정규 표현식.

    - window_regex `string`  
      선택 사항. `Win32` 컨트롤러가 창 제목을 검색할 때 사용하는 정규 표현식.

    - gamepad_type `string`  
      선택 사항. 가상 게임패드 유형. 값은 `Xbox360`, `DualShock4`(또는 `DS4`)이다. 제공하지 않으면 기본적으로 `Xbox360`을 사용한다.

    - screencap `string`  
      선택 사항. 스크린샷 방식. 제공하지 않으면 기본값을 사용한다. 창 정규 표현식이 구성된 경우에만 유효하다. 자세한 내용은 [제어 방식 설명](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/2.4-控制方式说明.md#win32-screencap)을 참고한다.

  - linux `object`  
    `Linux` 컨트롤러의 상세 구성. 자세한 내용은 [제어 방식 설명](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/2.4-控制方式说明.md#linux)을 참고한다.

    - screencap `string`  
      선택 사항. `Linux` 컨트롤러의 스크린샷 방식. 제공하지 않으면 기본값을 사용한다.

    - input `string`  
      선택 사항. `Linux` 컨트롤러의 입력 방식. 제공하지 않으면 기본값을 사용한다.

    - use_win32_vk_code `bool`
      선택 사항. `true`이면 키를 Win32 Virtual-Key 키 코드로 간주하여 내부적으로 Linux evdev 코드로 변환하고, `false`이면 원시 evdev 코드로 처리한다. 기본값은 `false`이다.

    - pipewire_source `string`  
      선택 사항. `PipeWire` 스크린샷의 스트림 소스: `Gamescope`는 gamescope 노드에 직접 연결(node id는 런타임에 탐색)하고, `Portal`은 xdg-desktop-portal ScreenCast를 사용한다. `screencap`이 `PipeWire`일 때만 유효하다. 기본값은 `Gamescope`이다.

- resource `object[]`  
  리소스 구성. 리소스 로드 정보를 담은 객체 배열이다.

  - name `string`  
    고유 이름 식별자. 리소스 패키지 ID로 사용된다.

  - label `string`  
    표시 이름. 사용자 인터페이스에 표시하는 데 사용된다. 국제화 문자열(`$`로 시작)을 지원한다. 설정하지 않으면 `name` 필드의 값을 표시한다. 선택 사항.

  - description `string`  
    리소스 상세 설명 정보. 파일 경로, URL 또는 직접 입력한 텍스트를 지원하며, 내용은 Markdown 형식을 지원한다. 선택 사항.

  - icon `string`  
    리소스 아이콘 파일 경로. 프로젝트 루트 디렉터리 기준 상대 경로이다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

  - path `string[]`  
    로드할 경로 배열. 여러 경로를 제공하면 순서대로 로드되며, 나중에 로드된 리소스가 먼저 로드된 리소스를 [덮어쓴다](#리소스-덮어쓰기).  
    파일의 상대 경로는 interface.json과 같은 디렉터리를 기준으로 한다.  
    주의: 리소스는 `pipeline`뿐 아니라 `image`와 `model`도 포함하므로 `pipeline` 디렉터리를 직접 지정하지 않는다.

  - controller `string[]`  
    선택 사항. 이 리소스 패키지가 지원하는 컨트롤러 유형 목록을 지정한다. 배열 요소는 `controller` 구성의 `name` 필드와 대응해야 한다. 지정하지 않으면 모든 컨트롤러 유형을 지원한다는 의미이다.  
    사용자가 특정 컨트롤러를 선택하면, 해당 컨트롤러를 지원하는 리소스 패키지만 사용자 인터페이스에 선택 가능하도록 표시된다. 이를 통해 컨트롤러 유형별로 특별히 최적화된 리소스 패키지를 제공할 수 있다.

  - option `string[]`  
    선택 사항. 리소스 패키지 수준의 옵션 구성. 문자열 배열이며, 배열 요소는 바깥쪽 option 구성의 키 이름과 대응해야 한다.  
    이 옵션이 생성하는 매개변수는 모든 작업의 pipeline override에 참여하여 리소스 패키지 수준의 매개변수 전달 역할을 한다.  
    참조된 option이 현재 controller/resource 조건을 지원하지 않으면, 해당 option의 `pipeline_override`(중첩된 `option.option` 포함)는 병합에 참여하지 않는다. **💡 v2.3.1**

  - hash `string` **💡 v2.6.0**  
    선택 사항. 리소스 무결성 검증 값. 이 값은 `path`만 로드한 뒤 `MaaResourceGetHash`로 얻은 hash 문자열이어야 한다.  
    검증 시점은 `path` 로드가 끝난 뒤, `controller.attach_resource_path`를 로드하기 전이다.  
    실제 hash가 이 값과 일치하지 않으면 사용자에게 경고(예: 리소스 패키지 재다운로드 권장)를 표시해야 하지만, 계속 사용하는 것을 막아서는 안 된다.  
    디버그 버전(예: 프리릴리스 버전)은 이 검증을 건너뛸 수 있다. 이 필드를 설정하지 않았다면 검증할 필요가 없다.
  
    ```jsonc
    "resource": [
        {
            "name": "Android专用资源",
            "label": "$Android专用资源",
            "controller": ["Android"],
            "path": ["resource_android"]
        },
        {
            "name": "通用资源",
            "label": "$通用资源",
            "path": ["resource"],
            "hash": "1a2b3c4d"
        }
    ]
    ```

- pretask `object | object[]` **💡 v2.7.0**  
  선택 사항. Controller 시작 전에 실행하는 사전 작업 구성. 단일 객체 또는 객체 배열이 될 수 있다. Client는 Controller를 생성하거나 연결하기 전에 이 프로그램들을 순서대로 시작하고 실행이 끝나기를 기다려야 한다. 사전 작업의 시작이 실패하거나 0이 아닌 종료 코드를 반환하면, Client는 이번 시작을 중단하고 사용자에게 오류를 보고해야 한다.  
  사전 작업의 CWD는 interface.json이 있는 디렉터리이다.  
  같은 `pretask` 필드는 최상위 `import`로 로드되는 다른 PI 조각 파일에도 나타날 수 있다. Client는 각 위치의 사전 작업을 하나의 순서 있는 목록으로 병합해야 한다. 먼저 주 `interface.json`의 항목을 실행하고(단일 객체는 한 항목으로 간주), 이어서 `import` 배열 순서대로 각 참조 파일의 `pretask`를 차례로 덧붙인다(배열이면 배열 순서대로, 단일 객체이면 한 항목으로 간주). 실제 실행 순서는 이렇게 병합된 목록과 같다.  

  - resource `string[]` **💡 v2.8.1**  
    선택 사항. 이 사전 작업이 지원하는 리소스 패키지 목록을 지정한다. 배열 요소는 `resource` 구성의 `name` 필드와 대응해야 한다. 지정하지 않으면 이 사전 작업이 모든 리소스 패키지에서 사용 가능하다는 의미이다. Client는 현재 리소스 패키지를 지원하지 않는 사전 작업을 숨기거나, 사용 불가(회색/비활성) 상태로 표시하여 사용자에게 알릴 수 있다.

  - controller `string[]` **💡 v2.8.1**  
    선택 사항. 이 사전 작업이 지원하는 컨트롤러 유형 목록을 지정한다. 배열 요소는 `controller` 구성의 `name` 필드와 대응해야 한다. 지정하지 않으면 이 사전 작업이 모든 컨트롤러 유형에서 사용 가능하다는 의미이다. Client는 현재 컨트롤러를 지원하지 않는 사전 작업을 숨기거나, 사용 불가(회색/비활성) 상태로 표시하여 사용자에게 알릴 수 있다.

  - exec `string`  
    필수. 실행할 프로그램 경로. 시스템 `PATH`에 있는 실행 파일일 수 있으며, 예를 들어 `"python"`이 가능하다.

  - args `string[]`  
    선택 사항. 고정 인자 배열. 순서대로 `exec`에 전달된다.

  - name `string`  
    선택 사항. 사전 작업의 고유 식별자. 프로젝트 내에서 중복되지 않는 것을 권장하며, Client가 설정 파일과 로그에서 서로 다른 사전 작업을 구분하기 쉽게 한다. `name`이 없으면 Client는 `exec`를 식별자로 대체할 수 있다.

  - label `string`  
    선택 사항. 사전 작업이 Client UI에 표시되는 이름. 국제화 문자열(`$`로 시작)을 지원한다. 설정하지 않으면 Client는 `name` 또는 `exec`로 대체할 수 있다.

  - description `string`  
    선택 사항. 사전 작업의 상세 설명. Client UI의 안내/Tooltip에 사용된다. 국제화 문자열, 파일 경로 또는 URL을 지원하며, 내용은 Markdown 형식을 지원한다(`task.description`과 같은 의미).

  - icon `string`  
    선택 사항. 사전 작업이 Client UI에 표시되는 아이콘 경로. interface.json이 있는 디렉터리 기준 상대 경로이다. 국제화 문자열을 지원한다.

  - option `string[]`  
    선택 사항. 사전 작업 구성 항목. 배열이며, 배열 요소는 바깥쪽 `option` 구성의 키 이름과 대응해야 한다. Client는 이 구성 항목들에 따라 사용자가 선택하도록 한다.  
    `option`이 설정되어 있으면, Client는 이 option들의 현재 값을 **한 줄의 압축 JSON 문자열**로 직렬화하여 마지막 인자로 자동 추가해야 하며, 위치는 `args` 뒤이다. 설정하지 않았거나 비어 있으면 이 JSON 인자를 추가하지 않는다.  
    이 JSON 객체는 option 키 이름을 필드 이름으로 하며, 값의 유형은 `preset.task[].option`의 `OptionValue`와 같다: `select` / `switch`는 `case.name` 문자열, `checkbox`는 `case.name` 문자열 배열, `input`은 입력 필드 `name`에서 문자열 값으로의 객체이다. 사용자의 선택으로 활성화된 하위 구성 항목(`option.option`)도 자신의 option 키 이름으로 이 객체에 추가해야 하며, 현재 `controller` / `resource` 제한을 만족하지 않는 option은 추가해서는 안 된다.  
    사전 작업 프로세스에 전달하는 JSON에서 `password`가 `true`인 필드는 (프로그램이 사용하도록) 여전히 복호화된 원문을 사용해야 하지만, Client는 이 JSON이나 그 안의 원문을 로그에 기록해서는 안 된다. **💡 v2.10.0**  
    `pretask.option`은 사전 작업 프로세스에 전달할 인자를 생성하는 데만 사용되며, `pipeline_override` 병합에는 참여하지 않는다.  

  **단일 pretask 예시:**

  ```jsonc
  "pretask": {
      "exec": "python",
      "args": [
          "./scripts/prepare.py",
          "--before-controller"
      ],
      "option": [
          "启动前配置"
      ]
  }
  ```

  사용자가 선택한 option 값이 다음과 같다면:

  ```json
  {
      "启动前配置": "清理缓存"
  }
  ```

  Client가 실제로 전달하는 인자는 다음과 같다:

  ```jsonc
  [
      "./scripts/prepare.py",
      "--before-controller",
      "{\"启动前配置\":\"清理缓存\"}"
  ]
  ```

  **여러 pretask 예시:**

  ```jsonc
  "pretask": [
      {
          "exec": "python",
          "args": ["./scripts/check_env.py"]
      },
      {
          "exec": "./tools/bootstrap",
          "args": ["--fast"],
          "option": ["启动前配置"]
      }
  ]
  ```

  **`import`로 pretask를 파일 단위로 나누어 관리하기:**

  `task`, `preset`과 마찬가지로 사전 작업도 별도 파일로 분리하여 `import`로 참조할 수 있다. 예를 들면:

  ```jsonc
  // interface.json
  {
      "import": [
          "pretask_common.json"
      ],
      "pretask": {
          "exec": "python",
          "args": ["./scripts/main_prepare.py"]
      }
  }
  ```

  ```jsonc
  // pretask_common.json
  {
      "pretask": [
          {
              "exec": "python",
              "args": ["./scripts/check_env.py"]
          }
      ]
  }
  ```

  병합 후 Client는 먼저 `main_prepare.py`를 실행하고, 이어서 `check_env.py`를 실행한 다음, Controller를 시작해야 한다.

- agent `object | object[]`  
  에이전트 구성. 단일 객체 또는 객체 배열이 될 수 있으며, 자식 프로세스(AgentServer)의 정보를 담는다. 여러 Agent를 동시에 구성하여 더 복잡한 자동화 시나리오를 구현할 수 있다.  
  **v2.5.0**부터 Client는 이 자식 프로세스를 시작할 때 규정에 따라 `PI_` 접두사가 붙은 환경 변수도 주입해야 한다. 자세한 내용은 아래 [Agent 자식 프로세스 환경 변수](#agent-subprocess-env-v25) 절을 참고한다.

  - child_exec `string`  
    자식 프로세스 경로. 시스템 경로에 있는 실행 파일이다. 예를 들어 환경 변수(시스템 변수, 사용자 변수)에 Python 경로가 있으면 `"python"`이라고 바로 쓸 수 있다.  
    CWD는 interface.json이 있는 디렉터리이다.

  - child_args `string[]`  
    선택 사항. 자식 프로세스 인자 배열.

  - identifier `string`  
    선택 사항. 연결 식별자. 통신 소켓을 만드는 데 사용된다. 입력하면 그 값이 사용되고, 그렇지 않으면 자동으로 생성된다.

  **단일 Agent 예시:**

  ```jsonc
  "agent": {
      "child_exec": "python",
      "child_args": [
          "./agent/main.py",              // 주의: cwd는 interface.json이 있는 디렉터리이다
          "--test-mode"                   // 고정 문자열, 그대로 전달된다
      ]
  }
  ```

  **여러 Agent 예시:**

  ```jsonc
  "agent": [
      {
          "child_exec": "python",
          "child_args": ["./agent/recognition.py"]
      },
      {
          "child_exec": "python",
          "child_args": ["./agent/action.py"]
      }
  ]
  ```

<a id="agent-subprocess-env-v25"></a>

### Agent 자식 프로세스 환경 변수 **💡 v2.5.0**

Agent가 MaaFramework 메인 프로세스와 분리되어 실행되면, 자식 프로세스는 범용 UI의 이름과 버전, 인터페이스 언어, 사용자가 현재 선택한 컨트롤러와 리소스 패키지 등의 정보를 자동으로 알 수 없다. 이러한 내용은 MaaFW C API의 일반 콜백에도 노출되지 않는다. 사용자 정의 인식/액션 등의 로직이 **Client 측 컨텍스트**와 **현재 PI 선택의 런타임 스냅샷**을 읽을 수 있도록, **Client**가 `agent` 자식 프로세스를 시작할 때 프로세스 환경에 다음 변수를 주입하도록 규정한다(이름은 모두 대문자, 값은 문자열).

| 변수 이름 | 설명 |
| ------ | ---- |
| `PI_INTERFACE_VERSION` | Client가 「PI 확장 기능」 측면에서 구현한 프로토콜 버전. **시맨틱 버전** 문자열(예: `v2.5.0`). 자식 프로세스는 이를 통해 특정 변수 묶음이나 동작에 의존할 수 있는지 판단할 수 있다. `interface.json`의 숫자 필드 `interface_version`(현재 `2`로 고정)과 **혼동하지 말 것**. |
| `PI_CLIENT_NAME` | 범용 UI / Client 이름 식별자. 예: `MFAA`, `MXU`, `VSCODE`, `MPE`, `MaaDebugger` 등. |
| `PI_CLIENT_VERSION` | Client 자체의 버전 번호(시맨틱 버전 문자열, Client가 정의). |
| `PI_CLIENT_LANGUAGE` | 현재 UI 언어 코드. 예: `zh_cn`, `en_us`(`languages`의 키 또는 Client의 규정과 일치하면 된다). |
| `PI_CLIENT_MAAFW_VERSION` | 해당 Client가 통합/패키징한 MaaFramework 라이브러리 버전(시맨틱 버전 문자열). |
| `PI_VERSION` | `interface.json` 최상위 `version` 필드와 같으며, **리소스 프로젝트** 버전 번호를 나타낸다. |
| `PI_CONTROLLER` | **한 줄 JSON 문자열**: 사용자가 현재 선택한 `controller` 배열 요소에 해당하는 전체 객체. i18n을 지원하는 모든 필드(예: `label`, `description` 등)는 **표시용 최종 텍스트**로 치환되어야 하며, `$`로 시작하는 번역 키 참조가 남아 있어서는 안 된다. |
| `PI_RESOURCE` | **한 줄 JSON 문자열**: 사용자가 현재 선택한 `resource` 배열 요소에 해당하는 전체 객체. 마찬가지로 i18n 해석을 마치며, 환경 변수로 전달하기 쉽도록 줄바꿈 없는 압축 JSON 형식이다. |

**규정 설명:**

- 어떤 정보가 현재 사용할 수 없는 경우 Client는 해당 변수를 설정하지 않거나 비워 둘 수 있다. 자식 프로세스는 오류에 대비하여 모든 변수가 존재한다고 가정해서는 안 된다.
- `PI_CONTROLLER` / `PI_RESOURCE`는 **현재 선택**만 설명한다. 실행 중에 컨트롤러나 리소스 패키지를 전환한 경우, Client는 자식 프로세스를 재시작하거나 규정된 시점에 환경을 업데이트해야 한다(재시작 여부는 Client 구현이 결정하며, 이 프로토콜은 강제하지 않는다).
- 변수 값은 운영체제의 환경 변수 길이 및 문자 집합 제한을 만족해야 하며, JSON은 압축 직렬화(minify)를 사용하는 것이 좋다.

**예시(값은 이스케이프를 표현한 것이며 실제로는 한 줄):**

```text
PI_INTERFACE_VERSION=v2.5.0
PI_CLIENT_NAME=MFAA
PI_CLIENT_VERSION=v1.0.0
PI_CLIENT_LANGUAGE=zh_cn
PI_CLIENT_MAAFW_VERSION=v5.9.0
PI_VERSION=v2.2.0
PI_CONTROLLER={"name":"Win32-Window","label":"Win32-默认","description":"默认控制器","type":"Win32","win32":{"class_regex":"UnityWndClass","window_regex":"Endfield","screencap":"Background","mouse":"SendMessageWithCursorPos","keyboard":"PostMessage"},"permission_required":true}
PI_RESOURCE={"name":"官服","label":"官服","path":["./resource"]}
```

- group `object[]` **💡 v2.4.0**  
  선택 사항. 작업 그룹 선언. 작업 그룹과 그 표시 속성을 선언하는 데 사용되는 객체 배열이다.

  - name `string`  
    그룹 고유 식별자. 그룹 ID로 사용된다. 작업은 `task.group`을 통해 이 이름을 참조한다.

  - label `string`  
    그룹 표시 이름. 사용자 인터페이스에 표시하는 데 사용된다. 국제화 문자열(`$`로 시작)을 지원한다. 설정하지 않으면 `name` 필드의 값을 표시한다. 선택 사항.

  - description `string`  
    그룹 상세 설명 정보. 사용자가 그룹의 용도를 이해하는 데 도움을 준다. 파일 경로, URL 또는 직접 입력한 텍스트를 지원하며, 내용은 Markdown 형식을 지원한다. 선택 사항.

  - icon `string`  
    그룹 아이콘 파일 경로. 프로젝트 루트 디렉터리 기준 상대 경로이다. 사용자 인터페이스에 표시하는 데 사용된다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

  - default_expand `boolean`  
    선택 사항이며 기본값은 `true`이다. 이 그룹이 Client에서 기본적으로 펼쳐지는지 여부.

  ```jsonc
  "group": [
      {
          "name": "daily",
          "label": "$日常任务",
          "description": "$日常任务说明",
          "icon": "groups/daily.png",
          "default_expand": true
      },
      {
          "name": "battle",
          "label": "$战斗任务"
      }
  ]
  ```

- task `object[]`  
  작업 구성. 실행 가능한 작업의 정보를 담은 객체 배열이다.

  - name `string`  
    작업 고유 식별자. 작업 ID로 사용된다.

  - label `string`  
    작업 표시 이름. 사용자 인터페이스에 표시하는 데 사용된다. 국제화 문자열(`$`로 시작)을 지원한다. 설정하지 않으면 `name` 필드의 값을 표시한다. 선택 사항.

  - entry `string`  
    작업 진입점. `pipeline`에서 시작점이 되는 `Node`의 이름이다.

  - default_check `boolean`  
    이 작업을 기본적으로 선택할지 여부. 선택 사항이며 기본값은 false이다. Client는 초기화할 때 이 값에 따라 해당 작업을 기본적으로 체크할지 결정한다.

  - description `string`  
    작업 상세 설명 정보. 사용자가 작업 기능을 이해하는 데 도움을 준다. 파일 경로, URL 또는 직접 입력한 텍스트를 지원하며, 내용은 Markdown 형식을 지원한다. 선택 사항.

  - icon `string`  
    작업 아이콘 파일 경로. 프로젝트 루트 디렉터리 기준 상대 경로이다. 사용자 인터페이스에 표시하는 데 사용된다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

  - group `string[]` **💡 v2.4.0**  
    선택 사항. 이 작업이 속한 그룹 목록을 지정한다. 배열 요소는 최상위 `group` 구성의 `name` 필드와 대응해야 한다. 지정하지 않으면 이 작업은 어떠한 명시적 그룹에도 속하지 않는다는 의미이다.

    하나의 작업이 동시에 여러 그룹에 속할 수 있다. Client는 이 값들을 그룹 소속 관계로만 취급해야 하며, 작업의 신원, 체크 상태, 프리셋 참조, 구성 항목 값은 여전히 `task.name`을 유일한 키로 한다.

    ```jsonc
    "task": [
        {
            "name": "领取奖励",
            "label": "$领取奖励",
            "entry": "CollectReward",
            "group": ["daily"]
        },
        {
            "name": "刷图",
            "label": "$刷图",
            "entry": "FarmStage",
            "group": ["daily", "battle"]
        }
    ]
    ```

  - resource `string[]`  
    선택 사항. 이 작업이 지원하는 리소스 패키지 목록을 지정한다. 배열 요소는 `resource` 구성의 `name` 필드와 대응해야 한다. 지정하지 않으면 이 작업이 모든 리소스 패키지에서 사용 가능하다는 의미이다.  
    사용자가 특정 리소스 패키지를 선택하면, Client는 해당 리소스 패키지를 지원하지 않는 작업을 숨기거나 사용 불가(회색/비활성) 상태로 표시하여 사용자에게 알릴 수 있다. 이를 통해 리소스 패키지별로 전용 작업 구성을 제공할 수 있으며, 예를 들어 이벤트 작업은 특정 리소스 패키지에서만 사용할 수 있다.

    ```jsonc
    "task": [
        {
            "name": "活动任务",
            "label": "$活动任务",
            "entry": "ActivityTask",
            "resource": ["Official"],
            "description": "仅在官服资源包中可用的活动任务"
        },
        {
            "name": "通用任务",
            "label": "$通用任务",
            "entry": "CommonTask"
        }
    ]
    ```

  - controller `string[]`  
    선택 사항. 이 작업이 지원하는 컨트롤러 유형 목록을 지정한다. 배열 요소는 `controller` 구성의 `name` 필드와 대응해야 한다. 지정하지 않으면 이 작업이 모든 컨트롤러 유형에서 사용 가능하다는 의미이다.  
    사용자가 특정 컨트롤러를 선택하면, Client는 해당 컨트롤러를 지원하지 않는 작업을 숨기거나 사용 불가(회색/비활성) 상태로 표시하여 사용자에게 알릴 수 있다. 이를 통해 컨트롤러 유형별로 전용 작업 구성을 제공할 수 있으며, 예를 들어 일부 작업은 Adb 컨트롤러에만, 일부 작업은 Win32 컨트롤러에만 적용할 수 있다.

    ```jsonc
    "task": [
        {
            "name": "安卓专属任务",
            "label": "$安卓专属任务",
            "entry": "AndroidOnlyTask",
            "controller": ["Android"],
            "description": "仅在安卓控制器中可用的任务"
        },
        {
            "name": "PC专属任务",
            "label": "$PC专属任务",
            "entry": "Win32OnlyTask",
            "controller": ["Win32Emulator"],
            "description": "仅在Win32控制器中可用的任务"
        },
        {
            "name": "通用任务",
            "label": "$通用任务",
            "entry": "CommonTask"
        }
    ]
    ```

  - pipeline_override `pipeline`  
    선택 사항. 작업 매개변수. 작업을 실행할 때 이미 로드된 리소스를 [덮어쓴다](#리소스-덮어쓰기). 이 항목의 구조는 `pipeline`의 `json` 파일과 완전히 같으며, 작업 이름 부분을 포함해야 한다. 예를 들면:

    ```jsonc
    "pipeline_override": {
        "Quit": {
            "enabled": true
        }
    }
    ```

  - option `string[]`  
    선택 사항. 작업 구성 항목. 이후의 `option` 객체에 있는 키들의 값을 담은 배열이며, Client는 요구에 따라 사용자가 선택하도록 한다.  
    Client는 `option`의 순서를 사용하여 구성 항목을 표시할 수 있다.

- option `record<string, object>`  
  구성 항목 정의. 구성 항목 정보를 담은 객체 맵이다.

  - _key_  
    고유 이름 식별자. 작업이 이 이름을 사용하여 참조한다.

  - type `string`  
    구성 항목 유형. 선택 사항이며 기본값은 `"select"`이다. 선택 가능한 값:
    - `"select"`: 드롭다운 선택 상자. 사용자가 미리 정의된 옵션 중 하나를 선택한다
    - `"checkbox"`: 다중 선택 상자. 사용자가 미리 정의된 옵션 중 여러 개를 선택한다 **💡 v2.3.0**
    - `"input"`: 사용자 입력 상자. 사용자가 내용을 직접 입력할 수 있다
    - `"hotkey"`: 단축키 캡처 상자. 사용자가 키 입력으로 단축키를 캡처할 수 있다 **💡 v2.8.0**
    - `"switch"`: 선택 상자, Yes or No

  - controller `string[]` **💡 v2.3.0**  
    선택 사항. 이 구성 항목이 적용되는 컨트롤러 유형 목록을 지정한다. 배열 요소는 `controller` 구성의 `name` 필드와 대응해야 한다. 지정하지 않으면 이 구성 항목이 모든 컨트롤러 유형에서 사용 가능하다는 의미이다.  
    사용자가 특정 컨트롤러를 선택하면, Client는 해당 컨트롤러에 적용되지 않는 구성 항목을 숨기거나 사용 불가(회색/비활성) 상태로 표시하여 사용자에게 알릴 수 있다.  
    현재 컨트롤러가 이 목록에 없으면 이 구성 항목은 비활성으로 간주한다. 그 자신과 하위 구성 항목(`option.option`)이 생성하는 모든 `pipeline_override`는 병합에 참여하지 않는다. **💡 v2.3.1**

  - resource `string[]` **💡 v2.3.0**  
    선택 사항. 이 구성 항목이 적용되는 리소스 패키지 목록을 지정한다. 배열 요소는 `resource` 구성의 `name` 필드와 대응해야 한다. 지정하지 않으면 이 구성 항목이 모든 리소스 패키지에서 사용 가능하다는 의미이다.  
    사용자가 특정 리소스 패키지를 선택하면, Client는 해당 리소스 패키지에 적용되지 않는 구성 항목을 숨기거나 사용 불가(회색/비활성) 상태로 표시하여 사용자에게 알릴 수 있다.  
    현재 리소스 패키지가 이 목록에 없으면 이 구성 항목은 비활성으로 간주한다. 그 자신과 하위 구성 항목(`option.option`)이 생성하는 모든 `pipeline_override`는 병합에 참여하지 않는다. **💡 v2.3.1**

  - label `string`  
    구성 항목 표시 레이블. 사용자 인터페이스에 표시하는 데 사용된다. 국제화 문자열(`$`로 시작)을 지원한다. 선택 사항.

  - description `string`  
    구성 항목 상세 설명 정보. 사용자가 구성 항목의 역할을 이해하는 데 도움을 준다. 파일 경로, URL 또는 직접 입력한 텍스트를 지원하며, 내용은 Markdown 형식을 지원한다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

  - icon `string`  
    구성 항목 아이콘 파일 경로. 프로젝트 루트 디렉터리 기준 상대 경로이다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

  - cases `object[]`  
    `type`이 `"select"`/`"checkbox"`/`"switch"`일 때만 사용한다. 선택 항목. 각 선택지의 정보를 담은 객체 배열이다.

    **주의:** `type`이 `"checkbox"`이면 사용자는 여러 case를 동시에 선택할 수 있으며, 선택된 모든 case의 `pipeline_override`는 `cases` 배열에 정의된 순서대로 차례로 병합되어 적용된다. 사용자가 체크한 순서와는 무관하다. `min_count` / `max_count`로 최소 / 최대 선택 개수를 제한할 수 있다. **💡 v2.10.1**

    **주의:** `type`이 `"switch"`이면 case를 두 개만 지원하며, 다음 규칙을 따라야 한다:
    - `case.name`이 `"Yes"`, `"yes"`, `"Y"`, `"y"` 중 하나이면 해당 case는 **Yes 선택지**로 인식된다
    - `case.name`이 `"No"`, `"no"`, `"N"`, `"n"` 중 하나이면 해당 case는 **No 선택지**로 인식된다
    - Client는 case의 name에 따라 사용자의 Y/N 입력을 매칭하며, 그 외의 입력은 다시 입력하도록 요구된다

    Client 간 일관성을 위해 두 case의 name으로 `"Yes"`와 `"No"`를 사용할 것을 권장한다.

    Client는 `cases`의 순서를 사용하여 선택지를 표시할 수 있다.

    - name `string`  
      선택지 고유 식별자. 선택지 ID로 사용된다.

    - label `string`  
      선택지 표시 이름. 사용자 인터페이스에 표시하는 데 사용된다. 국제화 문자열(`$`로 시작)을 지원한다. 설정하지 않으면 `name` 필드의 값을 표시한다. 선택 사항.

    - description `string`  
      선택지 상세 설명 정보. 파일 경로, URL 또는 직접 입력한 텍스트를 지원하며, 내용은 Markdown 형식을 지원한다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

    - icon `string`  
      선택지 아이콘 파일 경로. 프로젝트 루트 디렉터리 기준 상대 경로이다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

    - option `string[]`  
      하위 구성 항목 목록. 선택 사항. 사용자가 현재 선택지를 선택했을 때만 이 하위 구성 항목들이 표시된다. 이 하위 구성 항목들도 바깥쪽 `option`에 정의하며, 무한 중첩을 지원한다.

    - pipeline_override `pipeline`  
      `task`의 `pipeline_override`와 같으며, 선택지가 활성화되었을 때 적용된다.

  - inputs `object[]`  
    `type`이 `"input"`일 때만 사용한다. 입력 구성. 사용자가 입력할 수 있는 필드를 정의하는 객체 배열이다.

    - name `string`  
      입력 필드 고유 식별자. 입력 필드 ID로 사용된다.

    - label `string`  
      입력 필드 표시 이름. 사용자 인터페이스에 표시하는 데 사용된다. 국제화 문자열(`$`로 시작)을 지원한다. 설정하지 않으면 `name` 필드의 값을 표시한다. 선택 사항.

    - description `string`  
      입력 필드 상세 설명 정보. 사용자가 입력 요구 사항을 이해하는 데 도움을 준다. 파일 경로, URL 또는 직접 입력한 텍스트를 지원하며, 내용은 Markdown 형식을 지원한다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

    - default `string`  
      입력 필드의 기본값. 선택 사항. `password`가 `true`이면 이 필드를 설정할 수 없으며, JSON Schema가 해당 조합을 거부한다. **💡 v2.10.0**

    - pipeline_type `string`  
      입력 필드가 pipeline_override에서 갖는 데이터 유형. 선택 가능한 값: `"string"`, `"int"`, `"bool"`. pipeline_override의 변수 치환을 사용할 때 이 유형에 따라 형 변환을 수행한다.

    - verify `string`  
      사용자 입력이 유효한지 검증하는 정규 표현식. 선택 사항.

    - pattern_msg `string`  
      정규 표현식 검증에서 사용자 입력이 잘못되었을 때 표시하는 메시지. 선택 사항. 국제화(`$`로 시작)를 지원한다.

    - password `bool` **💡 v2.10.0**  
      선택 사항이며 기본값은 `false`이다. `true`이면 이 입력 필드를 비밀번호 / 키로 간주한다.

      Client는 다음 제약을 반드시 지켜야 한다:

      - **인터페이스:** 비밀번호 입력 상자(마스킹 표시)를 사용하며, UI에 원문을 표시해서는 안 된다. 저장된 값도 인터페이스에서 마찬가지로 마스킹하여 표시해야 한다.
      - **로그 및 원격 측정:** 원문을 로그, 원격 측정, 크래시 보고서 또는 공유 가능한 어떠한 출력에도 기록해서는 안 된다. 자리 표시가 필요하면 마스크(예: `******`)를 사용하거나 해당 필드를 아예 생략한다.
      - **구성 저장:** 사용자 구성 파일에 기록할 때는 반드시 암호화하여 저장해야 하며, 평문으로 디스크에 기록해서는 안 된다. 구성을 읽은 뒤에는 메모리에서만 복호화하여 `pipeline_override` 치환, `pretask` 인자 전달 등 런타임에서 사용한다.
      - **암호화 구현:** 알고리즘과 암호문 형식은 Client가 자체적으로 결정하며, 암호문이 Client 간 / 기기 간에 상호 복호화될 필요는 없다. 운영체제가 제공하는 자격 증명 보호(예: Windows DPAPI, macOS Keychain, Linux Secret Service)를 우선 사용할 것을 권장한다.
      - **`default` / `preset`:** 비밀번호 필드에는 `default`를 설정할 수 없다(JSON Schema는 `password: true`와 `default`가 동시에 나타나는 것을 거부한다). 리소스 작성자는 비밀번호 필드를 `preset`에 쓰지 않아야 한다. `interface.json`은 보통 리소스와 함께 배포되므로 평문 키가 그 안에 있어서는 안 된다.

  - hotkeys `object[]`  
    `type`이 `"hotkey"`일 때만 사용한다. 단축키 구성. 사용자가 캡처할 수 있는 단축키 필드를 정의하는 객체 배열이다. **💡 v2.8.0**

    Client는 단축키 캡처 컨트롤을 렌더링해야 한다. 사용자가 대상 키(또는 조합키)를 누르면, Client는 이를 사람이 읽을 수 있는 단축키 문자열(예: `"E"`, `"Ctrl+A"`)로 저장하며, 가상 키 코드나 JSON 배열을 직접 저장해서는 **안 된다**. 조합키는 `+`로 연결하고 **마지막 부분이 주 키**이며, 앞 부분은 차례로 수식 키이다(예: `Ctrl+Shift+A`에서 `A`가 주 키, `Ctrl`과 `Shift`가 수식 키).

    `pipeline_override`를 생성할 때 Client는 **현재 선택된 컨트롤러의 `type`**(예: `Win32`, `Adb`, `WlRoots`)에 따라 단축키 문자열을 해당 컨트롤러가 지원하는 가상 키 코드로 매핑해야 한다. 매핑 규칙은 [`ClickKey`](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/3.1-任务流水线协议.md#clickkey), [`KeyDown`](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/3.1-任务流水线协议.md#keydown) 등의 액션이 사용하는 키 코드 표와 일치해야 한다.

    - name `string`  
      단축키 필드 고유 식별자. 필드 ID로 사용된다.

    - label `string`  
      단축키 필드 표시 이름. 사용자 인터페이스에 표시하는 데 사용된다. 국제화 문자열(`$`로 시작)을 지원한다. 설정하지 않으면 `name` 필드의 값을 표시한다. 선택 사항.

    - description `string`  
      단축키 필드 상세 설명 정보. 사용자가 해당 단축키의 용도를 이해하는 데 도움을 준다. 파일 경로, URL 또는 직접 입력한 텍스트를 지원하며, 내용은 Markdown 형식을 지원한다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

    - default `string`  
      단축키 필드의 기본값. 선택 사항. 사람이 읽을 수 있는 단축키 문자열(예: `"E"`, `"1"`, `"Ctrl+A"`)을 직접 입력하며, 가상 키 코드를 입력할 필요는 없다. Client는 이를 바탕으로 컨트롤 표시를 초기화하며, 사용자가 다시 캡처한 뒤에도 저장되는 것은 여전히 단축키 문자열이어야 한다.

  - pipeline_override `pipeline`  
    구성 항목이 `"input"` 또는 `"hotkey"` 유형일 때 사용하며, 사용자 입력 내용의 치환 템플릿으로 쓰인다. 문자열 안에서 `{이름}` 형식으로 입력 필드 또는 단축키 필드의 값을 참조할 수 있다. 선택 사항.

    구성 항목이 `"hotkey"` 유형이면, Client는 플레이스홀더를 치환할 때 문자열이 아닌 **정수**(가상 키 코드)를 출력해야 한다. 지원하는 플레이스홀더 형식:

    | 플레이스홀더 | 의미 |
    | --- | --- |
    | `{이름}` | `{이름}.primary`와 동일 |
    | `{이름}.primary` | 조합키의 주 키 |
    | `{이름}.modifier1` | 첫 번째 수식 키(예: `Ctrl`) |
    | `{이름}.modifier2` | 두 번째 수식 키(예: `Alt`, `Shift`) |

    위 플레이스홀더의 치환 결과는 **단일 정수**(가상 키 코드)이며, `key`가 _int_ 인 키 액션에 적합하다. 예를 들면:

    ```jsonc
    "pipeline_override": {
        "__SomeActionKeyDown": {
            "key": "{UseTool.primary}"
        }
    }
    ```

    > [!NOTE]
    >
    > Pipeline 프로토콜에서 [`ClickKey`](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/3.1-任务流水线协议.md#clickkey)의 `key` 필드는 `list<int>`도 지원한다(한 번의 액션으로 여러 키를 차례로 누르는 것. 예: `[17, 65]`는 Ctrl+A). `hotkey` 플레이스홀더는 **오직** 단일 정수로만 치환되며 배열로 자동 확장되지 않는다. 일반적인 단일 키 재할당(예: 전투 스킬 `E`, `1`, `F1`)에는 `{이름}.primary`를 사용하면 된다. 조합키를 한 번의 `ClickKey` 배열 형태로 꼭 써야 한다면, Integrator가 pipeline에서 별도로 설계해야 한다(예: 키 코드 배열을 직접 쓰거나, 여러 `KeyDown`/`KeyUp` 노드로 나눔).

  - default_case `string` | `string[]`  
    기본 선택지 이름. 선택 사항.
    - `type`이 `"select"` / `"switch"`이면 단일 문자열을 입력하며, Client는 이 값을 선택지의 초기 선택 값으로 사용한다.
    - `type`이 `"checkbox"`이면 문자열 배열을 입력하며, Client는 이 값을 다중 선택 상자의 초기 선택 값으로 사용한다. **💡 v2.3.0**  
      `default_case`의 요소 개수는 `min_count` / `max_count`(설정된 경우)를 만족해야 한다. **💡 v2.10.1**

  - min_count `number` **💡 v2.10.1**  
    `type`이 `"checkbox"`일 때만 사용한다. 선택 사항이며 기본값은 `0`이다. 사용자가 최소한 선택해야 하는 case 개수로, 음이 아닌 정수이다.  
    `0`이면 선택하지 않아도 된다. 이 값은 `cases`의 길이보다 커서는 안 되며, `max_count`도 함께 설정된 경우 `max_count`보다 커서도 안 된다.  
    Client는 사용자가 선택할 때 검증해야 한다: 선택 개수가 `min_count`보다 적으면 사용자에게 추가 선택을 안내해야 하며, 하한을 만족하지 않는 선택으로 작업을 시작해서는 안 된다.

  - max_count `number` **💡 v2.10.1**  
    `type`이 `"checkbox"`일 때만 사용한다. 선택 사항. 사용자가 최대로 선택할 수 있는 case 개수로, 음이 아닌 정수이다. 설정하지 않으면 제한이 없다는 의미이다(모든 case를 선택할 수 있다).  
    이 값은 `cases`의 길이보다 커서는 안 되며, `min_count`도 함께 설정된 경우 `min_count`보다 작아서도 안 된다.  
    Client는 사용자가 선택할 때 `max_count`를 초과하는 체크를 막아야 한다.

- global_option `string[]` **💡 v2.3.0**  
  선택 사항. 전역 옵션 구성. 문자열 배열이며, 배열 요소는 `option` 구성의 키 이름과 대응해야 한다.  
  이 옵션이 생성하는 매개변수는 사용자가 어떤 리소스 패키지나 컨트롤러를 선택했는지와 상관없이 모든 작업의 pipeline override에 참여한다.  
  `resource.option` 및 `controller.option`과 달리, 전역 옵션은 어떤 리소스 패키지나 컨트롤러의 선택에도 의존하지 않는다.  
  다만 `global_option`이 참조하는 option은 여전히 그 option 자신의 `resource` / `controller` 제한을 만족해야 하며, 만족하지 않으면 어떠한 `pipeline_override`도 적용하지 않아야 한다. **💡 v2.3.1**

  ```jsonc
  "global_option": [
      "战斗划火柴",
      "战斗自动闪避"
  ]
  ```

- setting `object[]` **💡 v2.8.0**  
  선택 사항. 작업 설정 페이지 UI 선언. MXU 등의 Client가 전역 작업 구성 전용 설정 영역을 렌더링하는 데 사용된다.
  각 요소는 설정 구역 하나를 설명하며, Client는 배열 순서대로 각 구역을 렌더링할 수 있다.

  - name `string`  
    구역 고유 식별자. 구역 앵커와 내부 키로 사용된다.

  - label `string`  
    사용자 인터페이스에 표시되는 구역 이름. 국제화 문자열(`$`로 시작)을 지원한다. 설정하지 않으면 `name` 필드의 값을 표시한다. 선택 사항.

  - description `string`  
    구역 설명 텍스트. 파일 경로, URL 또는 직접 입력한 텍스트를 지원하며, 내용은 Markdown 형식을 지원한다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

  - icon `string`  
    구역 아이콘 파일 경로. 프로젝트 루트 디렉터리 기준 상대 경로이다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

  - option `string[]`  
    선택 사항. 최상위 `option` 구성에서 가져온, 순서가 있는 option 키 이름 목록. Client는 주어진 순서대로 이 option들을 렌더링해야 하며, 기존 `option` 프로토콜 정의를 재사용하여 실제 컨트롤로 삼아야 한다.

  - default_expand `boolean`  
    선택 사항이며 기본값은 `true`이다. 이 구역이 Client에서 기본적으로 펼쳐지는지 여부.

  ```jsonc
  "setting": [
      {
          "name": "task_global",
          "label": "$任务全局设置",
          "description": "$任务全局设置说明",
          "icon": "setting/task_global.png",
          "option": ["战斗划火柴", "战斗自动闪避"],
          "default_expand": true
      }
  ]
  ```

- import `string[]` **💡 v2.2.0**  
    선택 사항. 다른 PI 파일을 가져오는 경로 배열. 파일의 상대 경로는 interface.json과 같은 디렉터리를 기준으로 한다.  
    이 파일들의 `task`, `option`, `preset` **💡 v2.3.0**, `group` **💡 v2.4.0**, `pretask` **💡 v2.7.0**, `global_option` 및 `setting` **💡 v2.8.0** 필드를 가져오는 것을 지원한다.  
    Client는 이 파일들을 차례로 로드하고 그 내용을 현재 파일과 병합하여 구성의 분리와 재사용을 구현한다.

    **병합 규칙:**

    | 필드 | 병합 방식 |
    | --- | --- |
    | `task` | 주 파일 `task` 배열 끝에 추가 |
    | `option` | 객체 병합; 같은 이름의 키는 나중에 가져온 파일을 따른다 |
    | `global_option` | 주 파일 배열 끝에 추가; option 키 이름으로 중복 제거하며 먼저 나온 항목을 유지 **💡 v2.8.0** |
    | `setting` | 주 파일 `setting` 배열 끝에 추가 **💡 v2.8.0** |
    | `preset` | 주 파일 `preset` 배열 끝에 추가 |
    | `group` | 주 파일 `group` 배열 끝에 추가; `name`으로 중복 제거하며 먼저 나온 항목을 유지 |

- preset `object[]` **💡 v2.3.0**  
  선택 사항. 프리셋 구성. 객체 배열이다. 각 프리셋은 미리 정의된 작업 체크 상태와 옵션 값의 스냅샷이며, 사용자가 한 번에 적용하여 다양한 사용 시나리오를 빠르게 전환할 수 있다.

  - name `string`  
    고유 식별자. 프리셋 ID로 사용된다.

  - label `string`  
    표시 이름. 사용자 인터페이스에 표시하는 데 사용된다. 국제화 문자열(`$`로 시작)을 지원한다. 설정하지 않으면 `name` 필드의 값을 표시한다. 선택 사항.

  - description `string`  
    프리셋 상세 설명 정보. 사용자가 해당 프리셋의 적용 시나리오를 이해하는 데 도움을 준다. 파일 경로, URL 또는 직접 입력한 텍스트를 지원하며, 내용은 Markdown 형식을 지원한다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

  - icon `string`  
    프리셋 아이콘 파일 경로. 프로젝트 루트 디렉터리 기준 상대 경로이다. 선택 사항. 국제화(`$`로 시작)를 지원한다.

  - task `object[]`  
    프리셋에 포함된 작업 구성 목록.

    - name `string`  
      필수. 최상위 `task[].name`과 대응하는 작업 이름.

    - enabled `boolean`  
      선택 사항이며 기본값은 `true`이다. 프리셋에서 이 작업을 체크할지 여부.

    - option `record<string, OptionValue>`  
      선택 사항. 이 작업의 각 구성 항목에 대한 프리셋 값. 키는 최상위 `option`의 키 이름이다. `OptionValue`의 유형은 해당 `option`의 `type`에 따라 달라진다:

      | option.type | OptionValue 유형 | 예시 |
      | --- | --- | --- |
      | `select` / `switch` | `string`(`case.name`) | `"x3"` / `"Yes"` |
      | `checkbox` | `string[]`(`case.name` 배열) | `["自动战斗", "自动拾取"]` |
      | `input` | `record<string, string>`(입력 필드 name → 값) | `{ "章节号": "4" }` |
      | `hotkey` | `record<string, string>`(단축키 필드 name → 단축키 문자열) | `{ "FightCombo": "E" }` |

      `password`가 `true`인 입력 필드는 `preset`에 쓰지 않는다. **💡 v2.10.0**

  **프리셋 예시:**

  ```jsonc
  "preset": [
      {
          "name": "刷日常",
          "label": "$刷日常",
          "description": "每日例行套餐：荒原 + 心相 + 3-9 + 领奖",
          "icon": "preset_daily.png",
          "task": [
              { "name": "收取荒原", "enabled": true },
              { "name": "每日心相（意志解析）", "enabled": true },
              {
                  "name": "常规作战",
                  "enabled": true,
                  "option": {
                      "作战关卡": "3-9 厄险（百灵百验鸟）",   // select 유형: case.name을 입력
                      "复现次数": "x3",                       // select 유형: case.name을 입력
                      "刷完全部体力": "No",                   // switch 유형: case.name을 입력
                      "启用功能": ["自动战斗", "自动拾取"]    // checkbox 유형: case.name 배열을 입력
                  }
              },
              { "name": "领取奖励", "enabled": true },
              { "name": "活动：绿湖噩梦 17 艰难（活动已结束）", "enabled": false }
          ]
      },
      {
          "name": "实时辅助",
          "label": "$实时辅助",
          "description": "后台挂机辅助，仅执行自动辅助类任务",
          "task": [
              {
                  "name": "常规作战",
                  "enabled": true,
                  "option": {
                      "启用功能": ["自动战斗", "自动拾取", "自动回血"]
                  }
              }
          ]
      }
  ]
  ```

  **`import`로 프리셋을 파일 단위로 나누어 관리하기:**

  프리셋 구성은 `import`를 통해 별도 파일로 분리할 수 있어 관리와 재사용이 편리하다. 예를 들면:

  ```jsonc
  // interface.json
  {
      "import": [
          "preset_daily.json",
          "preset_realtime.json"
      ],
      "preset": [
          // 주 파일에서 프리셋을 직접 정의할 수도 있으며, 가져온 프리셋과 병합된다
      ]
  }
  ```

  ```jsonc
  // preset_daily.json
  {
      "preset": [
          {
              "name": "刷日常",
              "label": "$刷日常",
              "description": "每日例行套餐",
              "task": [
                  { "name": "收取荒原", "enabled": true },
                  { "name": "领取奖励", "enabled": true }
              ]
          }
      ]
  }
  ```

### Option 덮어쓰기 순서 **💡 v2.3.0**

각 수준의 option이 생성하는 `pipeline_override`는 다음 순서로 차례로 병합되며, **나중에 병합된 것이 먼저 병합된 같은 이름의 필드를 덮어쓴다**:

1. `global_option` — 전역 옵션. 가장 먼저 적용되며 우선순위가 가장 낮다
2. `resource.option` — 리소스 패키지 수준 옵션
3. `controller.option` — 컨트롤러 수준 옵션
4. `task.option` — 작업 수준 옵션. 가장 나중에 적용되며 우선순위가 가장 높다

즉: `task.option` > `controller.option` > `resource.option` > `global_option`.

위의 병합 순서에 들어가기 전에, 먼저 "비활성" option을 걸러내야 한다. 현재 `controller` / `resource` 조건을 만족하지 않는 모든 option(`global_option`, `resource.option`, `controller.option`, `task.option` 및 중첩된 `option.option`에서 온 것을 포함)은 `pipeline_override`를 생성해서는 안 된다. **💡 v2.3.1**

`pretask.option`은 위 덮어쓰기 순서에 참여하지 않는다. option의 현재 값을 사전 작업 프로세스의 마지막 인자로 직렬화하기만 한다. **💡 v2.7.0**

이렇게 설계한 이유는 더 구체적인 구성(작업 수준)일수록 더 높은 우선순위를 가져야 하고, 더 일반적인 구성(전역 수준)은 대체 기본값 역할을 해야 하기 때문이다.

**예시:**

`global_option`과 어떤 `task.option`이 같은 option을 동시에 참조하고, 그 option의 어떤 case가 같은 pipeline 노드에 서로 다른 override를 적용한다면, 작업 수준의 override가 최종적으로 적용된다.

### 구성 항목 예시

#### select 유형 옵션 예시

```jsonc
{
  "option": {
    "作战关卡": {
      "type": "select",
      "label": "$选择作战关卡",
      "description": "选择要刷的关卡",
      "default_case": "3-9 厄险",
      "cases": [
        {
          "name": "3-9 厄险（百灵百验鸟）",
          "label": "$3-9厄险",
          "description": "刷百灵鸟",
          "icon": "百灵鸟.png",
          "option": [
            "使用理智药",
            "刷完xxx"
          ],
          "pipeline_override": {
            "EnterTheShow": {
              "next": "MainChapter_3"
            }
          }
        }
      ]
    }
  }
}
```

#### input 유형 옵션 예시

```jsonc
{
  "option": {
    "自定义关卡": {
      "type": "input",
      "label": "自定义关卡",
      "description": "自己选打什么关",
      "icon": "扳手.png",
      "inputs": [
        {
          "name": "章节号",
          "label": "$章节号",
          "description": "关卡章节号，用阿拉伯数字表示",
          "default": "4",
          "pipeline_type": "string",
          "verify": "^\\d+$"
        },
        {
          "name": "超时时间",
          "label": "$超时时间",
          "description": "等待超时时间",
          "default": "20000",
          "pipeline_type": "int",
          "verify": "^\\d+$"
        }
      ],
      "pipeline_override": {
        "EnterTheShow": {
          "next": "MainChapter_{章节号}",
          "timeout": "{超时时间}"
        }
      }
    }
  }
}
```

#### password 입력 필드 예시 💡 v2.10.0

같은 `input` 옵션 안에 일반 필드와 비밀번호 필드를 함께 둘 수 있다. 비밀번호 필드에는 `default`를 입력하지 않는다.

```jsonc
{
  "option": {
    "账号登录": {
      "type": "input",
      "label": "$账号登录",
      "inputs": [
        {
          "name": "username",
          "label": "$用户名",
          "pipeline_type": "string"
        },
        {
          "name": "password",
          "label": "$密码",
          "pipeline_type": "string",
          "password": true
        }
      ],
      "pipeline_override": {
        "Login": {
          "custom_action_param": {
            "username": "{username}",
            "password": "{password}"
          }
        }
      }
    }
  }
}
```

#### checkbox 유형 옵션 예시 💡 v2.3.0

```jsonc
{
  "option": {
    "战斗划火柴": {
      "type": "checkbox",
      "label": "$战斗划火柴",
      "description": "选择要启用的划火柴功能，可多选",
      "min_count": 1,
      "max_count": 2,
      "default_case": ["普通划火柴", "蓄力划火柴"],
      "cases": [
        {
          "name": "普通划火柴",
          "label": "$普通划火柴",
          "description": "启用普通划火柴",
          "pipeline_override": {
            "NormalMatch": {
              "enabled": true
            }
          }
        },
        {
          "name": "蓄力划火柴",
          "label": "$蓄力划火柴",
          "description": "启用蓄力划火柴",
          "pipeline_override": {
            "ChargedMatch": {
              "enabled": true
            }
          }
        },
        {
          "name": "连续划火柴",
          "label": "$连续划火柴",
          "description": "启用连续划火柴",
          "pipeline_override": {
            "ComboMatch": {
              "enabled": true
            }
          }
        }
      ]
    }
  }
}
```

> **주의:** checkbox 유형에서 선택된 여러 case의 `pipeline_override`는 `cases` 배열의 **정의 순서**대로 차례로 병합되며, 사용자가 체크한 순서와는 무관하다.

### 국제화 지원

국제화를 지원하는 모든 문자열 필드에서, 문자열이 `$`로 시작하면 국제화 문자열이라는 뜻이며, Client는 번역 파일에서 실제 값을 읽어 표시해야 한다.

예를 들면:

```jsonc
{
  "name": "MyDemo3",
  "label": "$MyDemo3",
  "controller": [
    {
      "name": "Android",
      "label": "$安卓端"
    }
  ]
}
```

대응하는 번역 파일(예: `interface_zh.json`):

```jsonc
{
  "MyDemo3": "我的演示3",
  "安卓端": "安卓设备"
}
```

### 리소스 덮어쓰기

나중에 로드된 리소스에서 이미 로드된 리소스와 이름이 같은 작업이 발견되면 작업을 병합한다. 일반적으로 새 작업의 최상위 키가 기존 작업의 것을 대체한다고 볼 수 있다. 예를 들면:

기존 작업

```jsonc
{
    "task1": {
        "enabled": false,
        "recognition": "DirectHit",
        "next": [ "T1", "T2" ]
    }
}
```

새 작업

```jsonc
{
    "task1": {
        "enabled": true,
        "action": "Click",
        "next": [ "T2", "T3" ]
    }
}
```

병합된 작업

```jsonc
{
    "task1": {
        "enabled": true,
        "recognition": "DirectHit",
        "action": "Click",
        "next": [ "T2", "T3" ]       // 그대로 대체되며, 내부에서는 병합되지 않는다
    }
}
```

### 노드 알림 처리

MaaFramework는 작업을 실행하는 과정에서 콜백 함수를 통해 노드 알림을 보낸다. Client는 사용자에게 작업 실행 상태를 표시할 수 있도록 이에 대응하는 처리 로직을 구현해야 한다.

#### 콜백 함수 시그니처

Client는 알림을 받기 위한 콜백 함수를 등록해야 하며, 함수 시그니처는 [MaaDef.h](https://github.com/MaaXYZ/MaaFramework/blob/main/include/MaaFramework/MaaDef.h)를 참고한다:

```c
typedef void(MAA_CALL* MaaEventCallback)(
    void* handle,
    const char* message,
    const char* details_json,
    void* trans_arg
);
```

- **message**: 메시지 유형 식별자(예: `Node.Action.Starting`, `Node.Recognition.Succeeded` 등)
- **details_json**: 구체적인 데이터를 담은 JSON 문자열

#### 메시지 템플릿 메커니즘

리소스 작성자는 Pipeline의 `focus` 필드에서 메시지 템플릿을 구성할 수 있다. `focus`는 딕셔너리이며, 키는 메시지 유형, 값은 템플릿 문자열 또는 템플릿 객체이다. 템플릿 문자열은 파일 경로, URL 또는 직접 입력한 텍스트를 지원하고, 내용은 Markdown 형식을 지원하며, 국제화(`$`로 시작)를 지원한다. Client는 콜백을 받은 뒤 템플릿에 따라 플레이스홀더를 치환하고 지정된 방식으로 사용자에게 표시해야 한다. 객체 표기에서는 이번 노드 결과를 원격 측정 플랫폼에 업로드할지도 구성할 수 있다.

##### `focus` 값의 두 가지 표기

**축약형(순수 문자열):** `display: "log"`와 같으며, 내용은 실행 로그에만 표시된다. `trace`는 기본값을 사용한다.

```jsonc
"focus": {
    "Node.Action.Starting": "{name} 开始执行"
}
```

**전체 표기(객체):** `display`로 표시 채널을 지정하고, `trace`로 원격 측정 업로드 여부를 제어할 수 있다. **💡 v2.3.0**(`trace`는 **💡 v2.9.1**)

```jsonc
"focus": {
    "Node.Action.Starting": {
        "content": "{name} 开始执行",
        "display": "toast",
        "trace": false
    }
}
```

##### `display` 선택 가능한 값 **💡 v2.3.0**

| 값 | 설명 | 동작 특성 |
| ---- | ------ | ---------- |
| `"log"` | 실행 로그(**기본값**) | 로그 스트림에 추가되며 조작을 방해하지 않음 |
| `"toast"` | 앱 내 간단 알림 | 잠시 나타났다가 자동으로 사라지며 차단하지 않음 |
| `"notification"` | 시스템 수준 알림 | OS 알림 센터로 푸시되며, 앱이 백그라운드에 있을 때도 수신 가능 |
| `"dialog"` | 비차단식 대화 상자 | 정보 상자가 나타나며, 작업 파이프라인은 백그라운드에서 **계속 실행**됨 |
| `"modal"` | 차단식 팝업 | 나타나면 작업이 사용자의 확인을 기다리며 **일시 정지**되고, 사람의 개입이 필요한 시나리오에 적합 |

`display`는 배열을 지원하며, 같은 메시지를 여러 채널에 동시에 보낼 수 있다:

```jsonc
"focus": {
    "Node.Action.Succeeded": {
        "content": "✅ {name} 执行成功",
        "display": ["log", "toast"]
    },
    "Node.Action.Failed": {
        "content": "❌ 执行失败，请检查环境",
        "display": ["log", "modal"]
    }
}
```

##### `trace` 기본값 **💡 v2.9.1**

`telemetry.sentry`가 구성되어 있고 `tracing`이 활성화되어 있다는(또는 명시적으로 끄지 않았다는) 전제에서:

| 메시지 유형 | 기본값 | 설명 |
| -------- | ------ | ---- |
| `Node.PipelineNode.Failed` | `true` | 파이프라인 노드 실패에 대한 일반적인 Client의 기본 보고 동작과 맞춤 |
| 그 외 `Node.xxx` 메시지 | `false` | 해당 메시지의 템플릿 객체에 `"trace": true`를 명시적으로 써야 업로드됨 |

**Pipeline에서의 전체 구성 예시:**

```jsonc
{
  "NodeA": {
    "focus": {
      "Node.Recognition.Succeeded": "{name} 识别命中，准备开始执行",
      "Node.Action.Starting": {
        "content": "{name} 开始执行，任务 ID: {task_id}",
        "display": ["log", "toast"]
      },
      "Node.Action.Failed": {
        "content": "{name} 执行失败",
        "display": "modal",
        "trace": true
      },
      "Node.PipelineNode.Succeeded": {
        "trace": true
      }
    }
  }
}
```

**콜백 함수가 받는 인자 예시:**

```c
// message 인자:
"Node.Action.Starting"

// details_json 인자(파싱 후):
{
    "task_id": 12345,
    "action_id": 11111,
    "name": "NodeA",
    "focus": {
        "Node.Recognition.Succeeded": "{name} 识别命中，准备开始执行",
        "Node.Action.Starting": {
            "content": "{name} 开始执行，任务 ID: {task_id}",
            "display": ["log", "toast"]
        },
        "Node.Action.Failed": {
            "content": "{name} 执行失败",
            "display": "modal",
            "trace": true
        },
        "Node.PipelineNode.Succeeded": {
            "trace": true
        }
    }
}
```

#### Client 처리 흐름

1. 콜백 함수에서 `details_json` 인자를 파싱한다
2. 파싱된 객체에 `focus` 필드가 있는지 확인한다
3. 있으면 `message` 인자에 따라 `focus`에서 대응하는 템플릿(문자열 또는 객체)을 찾는다
4. 템플릿이 문자열이면 `content`는 그 문자열이고, `display`는 `["log"]`로 간주하며, `trace`는 기본값을 사용한다. 객체이면 `content`, `display`, `trace`를 각각 읽는다
5. `content`가 있으면 `details_json`의 데이터로 플레이스홀더(예: `{name}`, `{task_id}`)를 치환한 뒤, `display`가 지정한 채널을 통해 사용자에게 표시한다 **💡 v2.3.0**
6. 유효 `trace`를 결정한다: 객체에 명시적으로 주어졌으면 그 값을 사용하고, 그렇지 않으면 기본값을 사용한다. 전역 원격 측정이 활성화된 경우, 유효 값이 `true`일 때만 이번 노드 결과를 업로드한다 **💡 v2.9.1**

위 예시를 기준으로, `Node.Action.Starting`을 받으면 로그에 추가하고 toast를 띄워야 한다: `NodeA 开始执行，任务 ID: 12345`

#### 더 많은 메시지 유형

전체 콜백 메시지 목록과 상세 설명은 [콜백 프로토콜](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/2.3-回调协议.md)과 [MaaMsg.h](https://github.com/MaaXYZ/MaaFramework/blob/main/include/MaaFramework/MaaMsg.h)를 참고한다.
