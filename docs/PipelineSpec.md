# Pipeline 기술서

태스크 파이프라인(Pipeline)은 JSON으로 기술하는 노드(Node)의 집합이며, 각 노드의 인식(`recognition`), 동작(`action`), 후속 노드(`next`)가 태스크 흐름을 결정한다. 이 문서는 노드 필드와 규칙을 표 중심으로 요약한다. 원문은 [MaaFramework v5.14.3 docs/zh_cn/3.1-任务流水线协议.md](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/3.1-任务流水线协议.md)이다.

## 개요

### 구성

| 핵심 속성 | 의미 |
| --- | --- |
| `recognition` | 인식 알고리즘 |
| `action` | 실행할 동작 |
| `next` | 후속 노드 목록 |

그 밖의 확장 속성은 아래 [노드 공통 필드](#노드-공통-필드)에 정리한다. 자세한 형식은 [원본](PipelineProtocol.md#기본-형식)을 참고한다.

### 실행 흐름 요약

| 단계 | 내용 |
| --- | --- |
| 태스크 트리거 | `tasker.post_task`로 진입 노드를 지정해 태스크를 시작한다 |
| 순차 검사 | 현재 노드의 `next` 목록을 순서대로 인식한다. 한 라운드에서 모두 적중하지 않으면 타임아웃되거나 적중하는 노드가 나올 때까지 라운드를 반복한다 |
| 중단 | 어떤 하위 노드가 매칭되면 이후 노드의 검사를 즉시 종료하고, 매칭된 노드의 `action`을 실행한다 |
| 동작 성공 | 해당 노드의 `next` 목록으로 진입해 검사를 반복한다 |
| 동작 실패 | 해당 노드의 `on_error` 목록으로 진입한다 |
| `next` 인식 타임아웃 | 현재 노드의 `on_error` 목록으로 진입한다 |

노드 수명 주기: 노드 진입 → `pre_wait_freezes` → `pre_delay` → `action` → (`repeat` > 1이면 `repeat_wait_freezes` → `repeat_delay` → `action` 반복) → `post_wait_freezes` → `post_delay` → 스크린샷 → `next` 인식 → 성공 시 새 노드 진입, 실패 시 타이머 확인(타임아웃이면 `on_error`, 아니면 `rate_limit` 대기 후 스크린샷으로 복귀). 흐름도와 예시는 [원본](PipelineProtocol.md#노드-흐름)을 참고한다.

### 종료 조건

다음 중 하나라도 만족하면 태스크 흐름이 종료된다.

- 현재 노드의 `next` 목록이 비어 있다(`[JumpBack]` 복귀점이 존재하면 먼저 복귀한다)
- 현재 노드의 `next` 목록이 적중하지 못한 채 타임아웃되었다
- 외부에서 `post_stop`을 호출했거나 `StopTask` 동작이 실행되었다

## 노드 공통 필드

- 필수 필드는 Pipeline JSON 파일에서는 비워 둘 수 있으나 실제 실행 전에 인터페이스를 통해 설정해야 한다.
- 점(`.`)으로 시작하는 폴더와 JSON 파일은 읽지 않는다.
- `$`로 시작하는 JSON root field는 파싱하지 않는다.
- 모든 필드는 선택 사항이다.

### 인식·흐름 제어

| 필드 | 타입 | 기본값 | 용도 | 버전 |
| --- | --- | --- | --- | --- |
| `recognition` | string | `DirectHit` | 인식 알고리즘 유형 | - |
| `action` | string | `DoNothing` | 실행할 동작 | - |
| `next` | string \| NodeAttr \| list&lt;string \| NodeAttr&gt; | 비어 있음 | 이어서 실행할 노드 목록. 순서대로 인식해 처음 인식된 노드만 실행 | NodeAttr v5.1 |
| `on_error` | string \| NodeAttr \| list&lt;string \| NodeAttr&gt; | 비어 있음 | 이 노드의 `next`가 타임아웃되거나 동작이 실패한 뒤 실행할 노드 목록 | NodeAttr v5.1 |
| `rate_limit` | uint | 1000 | 인식 라운드 최소 소요 시간(ms). 부족분은 sleep으로 대기 | - |
| `timeout` | int | 20000 | 이 노드의 `next` 목록 인식 타임아웃(ms). `-1`은 무한 대기 | `-1` v5.5 |
| `inverse` | bool | false | 인식 결과를 반전 | - |
| `enabled` | bool | true | false이면 다른 노드의 `next` 목록에서 건너뜀 | - |
| `max_hit` | uint | UINT_MAX(무제한) | 인식에 성공할 수 있는 최대 횟수. 초과하면 `next` 목록에서 건너뜀 | v5.1 |
| `anchor` | string \| list&lt;string&gt; \| object | 비어 있음 | 인식 적중 및 동작 실행 시 앵커 이름이 이 노드를 가리키도록 설정 | v5.1 (object v5.7) |

- `recognition` 선택값: `DirectHit` | `TemplateMatch` | `FeatureMatch` | `ColorMatch` | `OCR` | `NeuralNetworkClassify` | `NeuralNetworkDetect` | `And` | `Or` | `Custom`. [알고리즘 유형](PipelineProtocol.md#알고리즘-유형)
- `action` 선택값: `DoNothing` | `Click` | `LongPress` | `Swipe` | `MultiSwipe` | `Scroll` | `ClickKey` | `LongPressKey` | `InputText` | `StartApp` | `StopApp` | `StopTask` | `Command` | `Shell` | `Screencap` | `Custom`. [동작 유형](PipelineProtocol.md#동작-유형)
- `next`/`on_error`는 속성이 있는 노드, NodeAttr 객체, 또는 둘을 섞은 배열을 지원한다. [노드 속성](PipelineProtocol.md#노드-속성)
- 현재 노드의 `recognition` 대기 시간·타임아웃 후 동작은 현재 노드가 아니라 이전 노드의 `timeout`·`on_error`로 조정한다.
- `timeout`은 대략 `while(!hit && !timeout) { foreach(next); sleep_until(rate_limit); }`로 동작한다.
- `inverse`로 반전된 노드는 실제로 아무것도 인식하지 않았으므로 Click 등의 자기 자신 클릭이 무효가 된다. 필요하면 `target`을 별도로 설정한다.
- `anchor` 형식: 문자열(현재 노드로 설정), 문자열 배열(여러 앵커를 모두 현재 노드로 설정), 객체(`{"A": "TargetNode", "B": ""}`: A를 TargetNode로 설정, 빈 문자열은 해제). 여러 노드가 같은 앵커를 설정하면 나중에 실행된 것이 덮어쓴다. `next`/`on_error`의 `[Anchor]` 속성으로 참조하며, 설정되지 않았거나 해제된 앵커를 참조한 노드는 건너뛴다.

### 지연·대기

실행 순서: `pre_wait_freezes` - `pre_delay` - `action` - `post_wait_freezes` - `post_delay`.

| 필드 | 타입 | 기본값 | 용도 | 버전 |
| --- | --- | --- | --- | --- |
| `pre_delay` | uint | 200 | 인식된 시점부터 동작 실행 전까지의 지연(ms) | - |
| `post_delay` | uint | 200 | 동작 실행 후부터 `next` 인식 전까지의 지연(ms) | - |
| `pre_wait_freezes` | uint \| object | 0(대기 안 함) | 인식된 시점부터 동작 실행 전까지 화면이 멈출 때까지 기다리는 시간(ms) | - |
| `post_wait_freezes` | uint \| object | 0(대기 안 함) | 동작 실행 후부터 `next` 인식 전까지 화면이 멈출 때까지 기다리는 시간(ms) | - |

- `*_wait_freezes`는 연속 지정 밀리초 동안 화면에 큰 변화가 없어야 다음으로 넘어간다. object 형식의 매개변수는 [화면 정지 대기](PipelineProtocol.md#화면-정지-대기)를 참고한다.
- 중간 과정 노드를 늘리고 지연은 적게 쓰는 것을 권장한다.

### 반복

| 필드 | 타입 | 기본값 | 용도 | 버전 |
| --- | --- | --- | --- | --- |
| `repeat` | uint | 1(반복 안 함) | 동작 반복 실행 횟수 | v5.3 |
| `repeat_delay` | uint | 0 | 반복되는 동작 사이의 지연(ms) | v5.3 |
| `repeat_wait_freezes` | uint \| object | 0(대기 안 함) | 반복되는 동작 사이에 화면이 멈출 때까지 기다리는 시간(ms) | v5.3 |

- 실행 흐름: `action` - [`repeat_wait_freezes` - `repeat_delay` - `action`] × (repeat-1).
- `repeat_delay`와 `repeat_wait_freezes`는 `repeat` > 1일 때만 적용되며, 두 번째 이후 동작 실행 전에 대기한다.
- 반복 도중 동작이 실패해도 중단하지 않으며 최종 결과는 마지막 동작을 기준으로 한다.

### 부가

| 필드 | 타입 | 기본값 | 용도 | 버전 |
| --- | --- | --- | --- | --- |
| `focus` | object | null(콜백 없음) | 관심 노드로 지정해 일부 콜백 메시지를 추가로 발생 | - |
| `attach` | object | 빈 객체 | 노드의 부가 설정을 저장하는 사용자 정의 JSON. 실행 로직에는 영향 없음 | v5.0 |

- `focus`의 메시지 유형별 값은 `string`(`display: "log"`와 동일) 또는 `object`(`display` 지정 가능)이다. [노드 알림](PipelineProtocol.md#노드-알림)
- `attach`는 기본값의 `attach`와 덮어쓰기가 아니라 딕셔너리 병합된다. 같은 키는 노드의 값이 우선하고 그 밖의 키는 유지된다.

## 좌표 필드 구분(roi/box/target)

| 필드 | 의미 | 비고 |
| --- | --- | --- |
| `roi` | 관심 영역(Region of Interest). 이미지 인식의 경계이며 이 영역 안에서만 이미지 처리를 수행 | 인식 범위는 `roi`와 `roi_offset`이 함께 결정 |
| `box` | 인식이 적중한 뒤 반환되는 매칭 영역("어디에서 인식되었는가") | - |
| `target` | 동작 실행 대상 영역("어디를 클릭/스와이프/스크롤할지") | 동작 대상은 `target`과 `target_offset`이 함께 결정. 기본값 `true`는 현재 인식의 `box`를 `target`으로 사용한다는 뜻이며, 고정 좌표·고정 영역·다른 노드를 지정할 수도 있음 |

흐름: `roi`(`roi_offset` 포함) 안에서 인식해 `box`를 얻고, `target`(`target_offset` 포함)을 계산한 뒤 동작을 실행한다. [원본](PipelineProtocol.md#roi--box--target-구분)

## Pipeline v2 표기

- MaaFW v4.4.0부터 지원하며 v1과 호환된다.
- v1과의 차이는 `recognition`과 `action` 관련 필드를 2단계 딕셔너리로 옮긴 것뿐이다. 유형은 `type`에, 나머지 매개변수는 `param`에 둔다. 키와 값은 변하지 않는다.
- `recognition`·`action` 이외의 필드(`next`, `pre_delay` 등)는 v1과 같다.

| 구분 | v1 | v2 |
| --- | --- | --- |
| 인식 | `"recognition": "TemplateMatch", "template": "A.png"` | `"recognition": {"type": "TemplateMatch", "param": {"template": "A.png"}}` |
| 동작 | `"action": "Click", "target": "XXX"` | `"action": {"type": "Click", "param": {"target": "XXX"}}` |

[원본](PipelineProtocol.md#pipeline-v2)

## 기본 속성

`default_pipeline.json`(v5.3)은 모든 노드와 특정 알고리즘/동작 유형에 기본 매개변수를 설정해 중복 설정을 줄인다. 리소스 로드 시 자동으로 읽히며 설정은 모든 노드에 상속된다.

| 최상위 객체 | 설정 대상 |
| --- | --- |
| `Default` | 모든 노드 공통 필드의 기본값(`rate_limit`, `timeout`, `pre_delay`, `post_delay` 등) |
| 알고리즘 이름 객체(`TemplateMatch`, `OCR`, `FeatureMatch` 등) | 해당 인식 알고리즘 유형의 기본 매개변수 |
| 동작 이름 객체(`Click`, `Swipe`, `StartApp` 등) | 해당 동작 유형의 기본 매개변수 |

알고리즘/동작 객체는 v1 또는 v2 형식으로 작성할 수 있다.

### 상속 우선순위

높은 순서대로 다음과 같다.

1. 노드에 직접 정의된 매개변수
2. `default_pipeline.json`에서 해당 알고리즘/동작 유형의 기본 매개변수
3. `default_pipeline.json`의 `Default` 객체의 기본 매개변수
4. 프레임워크 내장 기본값

### 주의 사항

- `default_pipeline.json`은 리소스 번들(Bundle)의 루트 디렉터리, 즉 `pipeline` 폴더와 같은 계층에 둔다.
- 알고리즘/동작 객체의 키 이름은 해당 유형 이름과 대소문자까지 완전히 일치해야 한다.
- `attach`는 덮어쓰기가 아니라 딕셔너리 병합된다.
- 기본 설정이 필요하지 않으면 노드에서 다른 값으로 명시적으로 설정해 덮어쓴다.

### 다중 Bundle 로드

- 각 Bundle의 `default_pipeline.json`은 순서대로 병합되며, 나중에 로드된 같은 이름의 필드가 덮어쓴다.
- 이미 로드된 노드는 이후 Bundle의 `default_pipeline.json`의 영향을 받지 않는다. 각 노드는 처음 로드될 때의 병합된 기본값을 유지한다.
- 각 Bundle의 `image` 폴더에서 같은 경로의 이미지는 나중에 로드된 Bundle을 기준으로 한다. 파일이면 마지막 Bundle의 것만 사용하고, 폴더이면 상대 경로 기준으로 병합하되 상대 경로가 같은 파일은 나중 Bundle의 것을 취한다.
- 특수 설정이 필요한 노드는 별도 Bundle로 분리하고 전용 `default_pipeline.json`을 두면 설정을 격리할 수 있다. 예: `MaaResourcePostPath(resource, "resource/base")` 다음 `MaaResourcePostPath(resource, "resource/debug")`.

예시와 상세는 [원본](PipelineProtocol.md#기본-속성)을 참고한다.

## 버전별 변경

| 버전 | 변경 내용 |
| --- | --- |
| v5.0 | `attach` 필드 추가; `TouchDown` `TouchMove` `TouchUp` `KeyDown` `KeyUp` 동작 추가; Click / LongPress / Swipe / MultiSwipe에 `contact` `pressure` 필드 추가; `target`에 `[x, y]` 2원 좌표 지원 추가 |
| v5.1 | `anchor` `max_hit` 필드 추가; `Scroll` 동작 추가; 노드 속성(`jump_back` / `anchor`) 추가; `next` / `on_error`에 NodeAttr 지원 추가; `order_by`에 `Expected` 정렬 추가 |
| v5.3 | `repeat` `repeat_delay` `repeat_wait_freezes` 필드 추가; `And` `Or` 인식 유형 추가; `Shell` 동작 추가; TemplateMatch `method`에 `10001` 추가; 기본 속성(`default_pipeline.json`) 추가 |
| v5.5 | `timeout`에 `-1`(무한 대기) 지원 추가; Scroll에 `target` `target_offset` 추가 |
| v5.6 | `roi` / `target`이 음수 좌표와 크기를 지원 |
| v5.7 | `anchor`에 object 형식(대상 노드 지정 / 앵커 해제) 추가; `And` / `Or`에 노드 이름 참조 지원 추가 |
| v5.8 | OCR에 `color_filter` 필드 추가; Shell `timeout`을 `shell_timeout`으로 이름 변경; `Screencap` 동작 추가 |
| v5.9 | `roi` / `target`의 string 형식에 `[Anchor]앵커이름` 참조 지원 추가; action 실패 시 `[JumpBack]` 유무에 따라 동작이 일치하지 않던 문제 수정(오류 처리 경로에서는 복귀를 트리거하지 않음) |
| v5.10 | `TouchDown` / `KeyDown`에 `auto_up` 필드 추가. 태스크 중지·종료 또는 컨트롤러 소멸 시 아직 눌려 있는 터치 포인트/키를 자동으로 뗀다 |

## 인식 알고리즘

노드의 `recognition`에 지정하는 알고리즘 10종이다.

| 알고리즘 | 한 줄 용도 | 언제 쓰나 | 핵심 필드 | 비용/특징 |
| --- | --- | --- | --- | --- |
| `DirectHit` | 인식 없이 곧바로 동작 실행 | 인식이 필요 없는 단계 | `roi`, `roi_offset` | 인식을 수행하지 않음 |
| `TemplateMatch` | 템플릿 매칭("이미지 찾기") | 화면에서 특정 이미지를 찾을 때 | `template`, `threshold`, `method` | `method`에 따라 속도/강건성 차이 |
| `FeatureMatch` | 특징 매칭(일반화 능력이 강한 "이미지 찾기") | 원근·크기 변화가 있는 이미지를 찾을 때 | `template`, `count`, `detector`, `ratio` | 원근·크기 변화에 강함, `detector`에 따라 속도/정밀도 차이 |
| `ColorMatch` | 색상 매칭("색 찾기") | 특정 색의 픽셀 영역을 찾을 때 | `method`, `lower`, `upper`, `count`, `connected` | 색상 공간(RGB/HSV/GRAY)을 `method`로 선택 |
| `OCR` | 문자 인식 | 화면의 글자를 읽거나 기대 문자열을 확인할 때 | `expected`, `threshold`, `replace`, `model`, `color_filter` | 모델 폴더(`rec.onnx`, `det.onnx`, `keys.txt`) 필요 |
| `NeuralNetworkClassify` | 딥러닝 분류 | **고정된 위치**가 기대하는 클래스인지 판단할 때 | `model`, `labels`, `expected` | ONNX 모델 필요, 위치 고정 |
| `NeuralNetworkDetect` | 딥러닝 객체 검출 | 임의의 위치에 있는 대상을 찾을 때 | `model`, `labels`, `expected`, `threshold` | 분류보다 학습 비용·추론 비용이 몇 배 큼 |
| `And` | 조합 인식(논리 AND) | 여러 조건이 모두 만족될 때 | `all_of`, `box_index`, `sub_name` | 모든 하위 인식이 적중해야 성공 (v5.3) |
| `Or` | 조합 인식(논리 OR) | 여러 조건 중 하나라도 만족될 때 | `any_of` | 첫 적중에서 성공하고 이후 인식을 중단 (v5.3) |
| `Custom` | 등록한 사용자 인식기 실행 | 기본 알고리즘으로 부족할 때 | `custom_recognition`, `custom_recognition_param` | `MaaResourceRegisterCustomRecognition`으로 등록한 핸들 실행 |

### 공통 인식 필드

여러 알고리즘이 공유한다. 알고리즘 절에서는 사용하는 필드 이름만 적는다.

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `roi` | *array<int, 4>* \| *string* | [0, 0, 0, 0] (전체 화면) | 아니오 | 관심 영역. 이 영역 안에서만 이미지 처리를 수행한다. *array*는 [x, y, w, h]이며 음수를 지원한다(x/y가 음수면 오른쪽/아래쪽 가장자리 기준, w/h가 0이면 가장자리까지 확장, 음수면 절댓값을 취하고 (x, y)를 우하단 모서리로 간주). *string*은 이전에 실행된 노드 이름으로, 그 노드가 인식한 대상 범위 안에서 인식하며 `[Anchor]앵커이름`으로 앵커에 대응하는 노드도 참조할 수 있다. 참조한 노드 또는 앵커의 인식 결과가 비어 있으면 인식 실패이다. | 음수 좌표 v5.6, `[Anchor]` 참조 v5.9 |
| `roi_offset` | *array<int, 4>* | [0, 0, 0, 0] | 아니오 | `roi`를 기준으로 추가 이동시킬 값. 네 값을 각각 더한다. | |
| `order_by` | *string* | `Horizontal` | 아니오 | 결과 정렬 방식. 선택 가능한 값은 알고리즘마다 다르며 `index`와 함께 쓴다. 값 설명은 [원본](PipelineProtocol.md#horizontal) 참고. | |
| `index` | *int* | 0 | 아니오 | 몇 번째 결과를 적중으로 삼을지. 결과가 N개면 범위는 [-N, N - 1]이고, 음수는 N - index로 변환한다. 범위를 벗어나면 결과 없음으로 간주한다. | |

### `DirectHit`

바로 적중시킨다. 인식을 수행하지 않고 곧바로 동작을 실행한다.

쓰는 곳: 인식 없이 동작만 실행하는 노드.

공통 필드 사용: `roi`, `roi_offset`

고유 필드: 없음.

[원본](PipelineProtocol.md#directhit)

### `TemplateMatch`

템플릿 매칭, 즉 "이미지 찾기"이다.

쓰는 곳: 화면에서 특정 이미지를 찾는 경우.

공통 필드 사용: `roi`, `roi_offset`, `order_by`(`Horizontal` | `Vertical` | `Score` | `Random`), `index`

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `template` | *string* \| *list<string, >* | - | 예 | 템플릿 이미지 경로(`image` 폴더 기준 상대 경로). 폴더 경로를 주면 안의 모든 이미지를 재귀 로드한다. | |
| `threshold` | *double* \| *list<double, >* | 0.7 | 아니오 | 템플릿 매칭 임계값. 배열이면 길이가 `template` 배열과 같아야 한다. | |
| `method` | *int* | 5 | 아니오 | 템플릿 매칭 알고리즘(cv::TemplateMatchModes). 아래 표 참고. | 10001 v5.3 |
| `green_mask` | *bool* | false | 아니오 | true이면 이미지에서 녹색 RGB (0, 255, 0)으로 칠한 부분은 매칭하지 않는다. | |

| method | 알고리즘 이름 | 속도 | 색상 민감도 | 조명 강건성 | 적합한 시나리오 |
| ------ | ------- | ---- | --------- | --------- | ------- |
| 10001 | TM_SQDIFF_NORMED (Inverted) **v5.3** | 빠름 | 민감 | 나쁨 | 정밀 매칭, 임계값 설정이 쉬움 |
| 3 | TM_CCORR_NORMED | 보통 | 민감 | 보통 | 템플릿이 밝을 때 효과가 좋음 |
| 5 | TM_CCOEFF_NORMED | 비교적 느림 | 둔감 | 좋음 | **권장**, 임계값 설정이 쉬움 |

- 사용하는 이미지는 무손실 원본을 720p로 축소한 뒤 잘라낸 것이어야 한다.
- 10001은 TM_SQDIFF_NORMED의 반전 버전으로, 점수가 높을수록 더 잘 매칭된다.
- `green_mask`는 일반적인 배경 변화에는 보통 필요 없으며, 방해 영역만 가리고 주체의 가장자리 특징이 사라지지 않게 한다.

[원본](PipelineProtocol.md#templatematch)

### `FeatureMatch`

특징 매칭으로, 일반화 능력이 더 강한 "이미지 찾기"이다. 원근 변화와 크기 변화에 강하다.

쓰는 곳: 원근·크기 변화가 있는 이미지를 찾는 경우.

공통 필드 사용: `roi`, `roi_offset`, `order_by`(`Horizontal` | `Vertical` | `Score` | `Area` | `Random`), `index`

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `template` | *string* \| *list<string, >* | - | 예 | 템플릿 이미지 경로(`image` 폴더 기준 상대 경로). 폴더 경로를 주면 안의 모든 이미지를 재귀 로드한다. | |
| `count` | *uint* | 4 | 아니오 | 매칭된 특징점의 최소 개수(임계값). | |
| `green_mask` | *bool* | false | 아니오 | true이면 이미지에서 녹색 RGB (0, 255, 0)으로 칠한 부분은 매칭하지 않는다. | |
| `detector` | *string* | `SIFT` | 아니오 | 특징 검출기. 아래 표 참고. | |
| `ratio` | *double* | 0.6 | 아니오 | KNN 매칭 거리 비율 [0 - 1.0]. 클수록 매칭이 느슨해진다. | |

| 검출기 | 속도 | 스케일 불변성 | 회전 불변성 | 정밀도 | 적합한 시나리오 |
| ----- | ---- | --------- | --------- | ---- | ------- |
| SIFT | 느림 | 있음 | 있음 | 최고 | **권장**, 정밀도 요구가 높은 시나리오 |
| KAZE | 비교적 느림 | 있음 | 있음 | 높음 | 2D/3D 이미지, 가장자리 보존이 좋음 |
| AKAZE | 보통 | 있음 | 있음 | 비교적 높음 | 속도와 정밀도의 균형 |
| BRISK | 빠름 | 있음 | 있음 | 보통 | 실시간성 요구가 높은 시나리오 |
| ORB | 가장 빠름 | **없음** | 있음 | 비교적 낮음 | 템플릿과 대상의 크기가 같을 때 사용 |

- 템플릿은 최소 64x64 픽셀을 권장한다. 너무 작으면 특징점이 적어 매칭 실패나 오매칭이 생긴다.
- 템플릿에는 충분한 질감 디테일(가장자리, 모서리)이 있어야 한다. 단색·그라데이션 영역은 특징점이 드물다.
- 격자·줄무늬 같은 반복 질감이 많으면 특징점 매칭이 혼란스러워진다.

[원본](PipelineProtocol.md#featurematch)

### `ColorMatch`

색상 매칭, 즉 "색 찾기"이다.

쓰는 곳: 특정 색의 픽셀 영역을 찾는 경우.

공통 필드 사용: `roi`, `roi_offset`, `order_by`(`Horizontal` | `Vertical` | `Score` | `Area` | `Random`), `index`

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `method` | *int* | 4 (RGB) | 아니오 | 색상 매칭 방식(cv::ColorConversionCodes). 자주 쓰는 값: 4 (RGB, 3채널), 40 (HSV, 3채널), 6 (GRAY, 1채널). | |
| `lower` | *list<int, >* \| *list<list<int, >>* | - | 예 | 색상 하한값. 가장 안쪽 list의 길이는 `method`의 채널 수와 같아야 한다. | |
| `upper` | *list<int, >* \| *list<list<int, >>* | - | 예 | 색상 상한값. 가장 안쪽 list의 길이는 `method`의 채널 수와 같아야 한다. | |
| `count` | *uint* | 1 | 아니오 | 조건에 맞는 픽셀 점의 최소 개수(임계값). | |
| `connected` | *bool* | false | 아니오 | true이면 색상 필터링 후 픽셀이 전부 연결된 가장 큰 덩어리만 카운트한다. false이면 연결 여부를 고려하지 않는다. | |

[원본](PipelineProtocol.md#colormatch)

### `OCR`

문자 인식이다.

쓰는 곳: 화면의 글자를 읽거나 기대 문자열을 확인하는 경우.

공통 필드 사용: `roi`, `roi_offset`, `order_by`(`Horizontal` | `Vertical` | `Area` | `Length` | `Random` | `Expected`), `index`

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `expected` | *string* \| *list<string, >* | 모든 결과 매칭 | 아니오 | 기대하는 결과. 정규식을 지원한다. | |
| `threshold` | *double* | 0.3 | 아니오 | 모델 신뢰도 임계값. | |
| `replace` | *array<string, 2>* \| *list<array<string, 2>>* | - | 아니오 | 인식 결과가 부정확한 문자를 치환한다. | |
| `only_rec` | *bool* | false | 아니오 | 인식만 수행한다(검출을 하지 않으므로 `roi`를 정확히 설정해야 한다). | |
| `model` | *string* | 비어 있음 | 아니오 | 모델 **폴더** 경로(`model/ocr` 기준 상대 경로). 비면 `model/ocr` 루트의 모델을 쓴다. 폴더에 `rec.onnx`, `det.onnx`, `keys.txt`가 있어야 한다. | |
| `color_filter` | *string* | 비어 있음 | 아니오 | `ColorMatch` 노드 이름. 그 노드의 `method`, `lower`, `upper`로 이미지를 이진화한 뒤 OCR에 넘긴다. | v5.8 |

- `color_filter`는 해당 노드의 색상 이진화 로직만 사용하며 `count`, `order_by` 등 결과 매개변수에는 의존하지 않는다.
- `color_filter`를 설정한 OCR 노드는 batch 최적화에 참여하지 않는다.

[원본](PipelineProtocol.md#ocr)

### `NeuralNetworkClassify`

딥러닝 분류로, 이미지의 **고정된 위치**가 기대하는 "클래스"인지 판단한다.

쓰는 곳: 화면의 고정된 위치에 나타나는 대상을 분류하는 경우.

공통 필드 사용: `roi`, `roi_offset`, `order_by`(`Horizontal` | `Vertical` | `Score` | `Random` | `Expected`), `index`

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `labels` | *list<string, >* | "Unknown"으로 채움 | 아니오 | 각 분류의 이름. 디버그 이미지와 로그 등에만 영향을 준다. | |
| `model` | *string* | - | 예 | 모델 파일 경로(`model/classify` 기준 상대 경로). 현재 ONNX만 지원한다. | |
| `expected` | *int* \| *string* \| *list\<int \| string\>* | 모든 결과 매칭 | 아니오 | 기대하는 분류 인덱스 또는 클래스 이름. 목록 안에 정수와 문자열을 섞을 수 있다. | |

- `labels`와 `expected`의 값은 모델의 실제 출력과 일치해야 한다.

[원본](PipelineProtocol.md#neuralnetworkclassify)

### `NeuralNetworkDetect`

딥러닝 객체 검출로, 고급 버전의 "이미지 찾기"이다. 분류기와 달리 임의의 위치를 지원한다.

쓰는 곳: 임의의 위치에 나타나는 대상을 찾는 경우.

공통 필드 사용: `roi`, `roi_offset`, `order_by`(`Horizontal` | `Vertical` | `Score` | `Area` | `Random` | `Expected`), `index`

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `labels` | *list<string, >* | 모델 metadata에서 읽음, 없으면 "Unknown" | 아니오 | 각 분류의 이름. 디버그 이미지와 로그 등에만 영향을 준다. metadata의 `names`, `name`, `labels`, `class_names`에서 읽기를 지원한다. | |
| `model` | *string* | - | 예 | 모델 파일 경로(`model/detect` 기준 상대 경로). YOLOv8, YOLOv11에서 내보낸 ONNX를 지원한다. | |
| `expected` | *int* \| *string* \| *list\<int \| string\>* | 모든 결과 매칭 | 아니오 | 기대하는 분류 인덱스 또는 클래스 이름. 목록 안에 정수와 문자열을 섞을 수 있다. | |
| `threshold` | *double* \| *list<double, >* | 0.3 | 아니오 | 모델 신뢰도 임계값. 배열이면 길이가 `expected` 배열과 같아야 한다. | |

- 분류기보다 모델 복잡도가 높아 학습 데이터·시간이 더 필요하고 추론 비용도 몇 배로 늘어난다.
- 입출력이 같은 다른 YOLO 모델은 이론상 지원할 수 있으나 테스트되지 않았다.
- `labels`와 `expected`의 값은 모델의 실제 출력과 일치해야 한다.

[원본](PipelineProtocol.md#neuralnetworkdetect)

### `And`

**v5.3** 조합 인식(논리 AND)이다. 모든 하위 인식이 적중해야 성공으로 간주한다.

쓰는 곳: 여러 조건이 동시에 만족되어야 하는 경우.

공통 필드 사용: 없음

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `all_of` | *list\<string \| object\>* | - | 예 | 하위 인식 목록. 요소는 노드 이름 참조(문자열) 또는 인라인 인식 정의(객체, v1/v2 호환·혼용 허용)이다. | 문자열 참조 v5.7 |
| `box_index` | *int* | 0 | 아니오 | 어느 하위 인식의 box를 현재 노드의 인식 box로 출력할지. `0 <= box_index < all_of.size`. | |
| `sub_name` | *string* | - | 아니오 | 하위 인식 별칭. 이후 하위 인식이 `roi: sub_name`으로 앞선 하위 인식의 `filtered`를 ROI로 참조할 수 있다. 같은 이름이면 마지막 것을 기준으로 하며 현재 노드 안에서만 유효하다. | |

- Pipeline v2에서는 이 필드들을 `recognition.param` 안에 넣는다.

[원본](PipelineProtocol.md#and)

### `Or`

**v5.3** 조합 인식(논리 OR)이다. 첫 번째로 적중한 것이 있으면 성공하며, 이후에는 인식하지 않는다.

쓰는 곳: 여러 조건 중 하나만 만족해도 되는 경우.

공통 필드 사용: 없음

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `any_of` | *list\<string \| object\>* | - | 예 | 하위 인식 목록. 요소는 노드 이름 참조(문자열) 또는 인라인 인식 정의(객체, v1/v2 호환·혼용 허용)이다. 첫 적중에서 성공하고 이후는 인식하지 않는다. | 문자열 참조 v5.7 |

- Pipeline v2에서는 이 필드를 `recognition.param` 안에 넣는다.

[원본](PipelineProtocol.md#or)

### `Custom`

`MaaResourceRegisterCustomRecognition` 인터페이스로 전달된 인식기 핸들을 실행한다.

쓰는 곳: 기본 알고리즘으로 표현할 수 없는 인식을 직접 구현해 등록한 경우.

공통 필드 사용: `roi`(`MaaCustomRecognitionCallback`.`roi`로 전달, 기본값 [0, 0, 0, 0]), `roi_offset`

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `custom_recognition` | *string* | - | 예 | 등록 인터페이스에 전달한 인식 이름. `MaaCustomRecognitionCallback`.`custom_recognition_name`으로도 전달된다. | |
| `custom_recognition_param` | *any* | `null` | 아니오 | 임의 타입의 인식 매개변수. `MaaCustomRecognitionCallback`.`custom_recognition_param`으로 전달된다. | |

[원본](PipelineProtocol.md#custom)

## 동작

노드가 인식에 성공한 뒤 수행하는 `action`의 유형 21종이다. 상세는 [원본](PipelineProtocol.md#동작-유형)을 따른다.

| 분류 | 동작 | 한 줄 용도 | 언제 쓰나 | 핵심 필드 |
| --- | --- | --- | --- | --- |
| 없음 | `DoNothing` | 아무것도 하지 않는다 | 인식만 하고 넘어갈 때 | (없음) |
| 포인터 | `Click` | 클릭 | 인식된 위치나 지정 좌표를 누를 때 | `target`, `target_offset`, `contact`, `pressure` |
| 포인터 | `LongPress` | 길게 누르기 | 지속 시간이 필요한 누르기 | `target`, `duration` |
| 포인터 | `Swipe` | 직선 스와이프 | 시작점에서 종점(경유점 가능)으로 끌 때 | `begin`, `end`, `duration`, `end_hold`, `only_hover` |
| 포인터 | `MultiSwipe` | 멀티 핑거 직선 스와이프 | 여러 손가락 스와이프를 시차를 두고 실행할 때 | `swipes`, `starting` |
| 포인터 | `TouchDown` | 터치 포인트를 누른다 | `TouchMove`/`TouchUp`과 조합한 사용자 정의 터치 | `contact`, `target`, `pressure`, `auto_up` |
| 포인터 | `TouchMove` | 터치 포인트를 이동한다 | 눌린 터치 포인트 위치 갱신 | `TouchDown`과 동일 |
| 포인터 | `TouchUp` | 터치 포인트를 뗀다 | `TouchDown`으로 만든 터치 종료 | `contact` |
| 포인터 | `Scroll` | 마우스 휠 스크롤 | Win32/macOS 등 휠 조작 | `target`, `dx`, `dy` |
| 키 | `ClickKey` | 키를 한 번 누른다 | 단발 키 입력 | `key` |
| 키 | `LongPressKey` | 키를 길게 누른다 | 지속 시간이 필요한 키 입력 | `key`, `duration` |
| 키 | `KeyDown` | 키를 누르되 떼지 않는다 | `KeyUp`과 조합한 사용자 정의 키 타이밍 | `key`, `auto_up` |
| 키 | `KeyUp` | 키를 뗀다 | `KeyDown`으로 만든 키 상태 종료 | `key` |
| 키 | `InputText` | 텍스트를 입력한다 | 문자열 입력 | `input_text` |
| 앱·태스크 | `StartApp` | App을 실행한다 | 앱 진입점 실행 | `package` |
| 앱·태스크 | `StopApp` | App을 종료한다 | 앱 종료 | `package` |
| 앱·태스크 | `StopTask` | 현재 태스크 체인을 중지한다 | 이후 인식 루프를 끝낼 때 | (없음) |
| 시스템·외부 | `Command` | 로컬 프로그램을 실행한다 | 외부 프로그램·스크립트 호출 | `exec`, `args`, `detach` |
| 시스템·외부 | `Shell` | ADB 기기에서 shell 명령을 실행한다 | ADB 컨트롤러에서 기기 명령 실행 | `cmd`, `shell_timeout` |
| 시스템·외부 | `Screencap` | 현재 스크린샷을 파일로 저장한다 | 스크린샷 보관 | `filename`, `format`, `quality` |
| 시스템·외부 | `Custom` | 등록된 사용자 동작을 실행한다 | `MaaResourceRegisterCustomAction`으로 등록한 동작 호출 | `custom_action`, `custom_action_param`, `target` |

### 공통 동작 필드

여러 동작이 공유하는 필드이다. 각 동작 절에는 사용하는 필드 이름만 적는다.

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `target` | true \| string \| array<int, 2> \| array<int, 4> | true | 아니오 | 동작 대상의 위치 | `Scroll`의 `target`은 v5.5 |
| `target_offset` | array<int, 4> | [0, 0, 0, 0] | 아니오 | `target`을 기준으로 네 값을 각각 더해 이동시킨 값을 대상으로 사용 | `Scroll`의 `target_offset`은 v5.5 |
| `contact` | uint | 0 | 아니오 | 접점 번호. 서로 다른 터치 포인트를 구분 | v5.0 (`TouchDown`/`TouchUp`의 `contact`는 표기 없음) |
| `pressure` | int | 1 | 아니오 | 접점 압력 | v5.0 |

`target` 값의 의미:

- `true`: 이 노드에서 방금 인식된 위치(자기 자신).
- `string`: 노드 이름. 이전에 실행된 노드가 인식한 위치. `[Anchor]앵커이름` 형식으로 앵커에 대응하는 노드를 참조할 수 있다 (v5.9). 참조한 노드 또는 앵커의 인식 결과가 비어 있으면 동작 실패.
- `array<int, 2>`: 고정 좌표점 `[x, y]` (v5.0). 음수는 오른쪽/아래쪽 가장자리 기준 (v5.6).
- `array<int, 4>`: 고정 좌표 영역 `[x, y, w, h]`. 영역 안에서 무작위로 점을 고르며 중심일 확률이 높다. 음수의 의미는 `roi`와 같다 (v5.6). `Scroll`은 전체 화면을 원하면 [0, 0, 0, 0]으로 설정할 수 있다.

`contact` 값의 의미 (컨트롤러별):

| 컨트롤러 | 의미 |
| --- | --- |
| Adb | 손가락 번호 (0은 첫 번째 손가락, 최대 10을 넘을 수 없음) |
| Android Native | 손가락 번호 (범위 0–15, Android MotionEvent pointer id에 대응) |
| Win32 | 마우스 버튼 번호 (0 왼쪽, 1 오른쪽, 2 가운데, 3 XBUTTON1, 4 XBUTTON2) |
| MacOS | 마우스 버튼 번호 (0 왼쪽, 1 오른쪽, 2 가운데) |

### `DoNothing`

아무것도 하지 않는다.

- 필드: 없음

### `Click`

클릭이다.

- 쓰는 곳: 가장 기본적인 포인터 동작. `target`의 정의는 다른 동작이 `Click`.`target`으로 참조한다.
- 공통 필드 사용: `target`, `target_offset`, `contact`, `pressure`
- 고유 필드: 없음

### `LongPress`

길게 누르기이다.

- 공통 필드 사용: `target`, `target_offset`, `contact`, `pressure`

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `duration` | uint | 1000 | 아니오 | 길게 누르는 지속 시간(ms) | - |

### `Swipe`

직선 스와이프이다.

- 공통 필드 사용: `contact`, `pressure` (`begin`/`end`의 값 형식은 `target`과 같다)

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `begin` | true \| string \| array<int, 2> \| array<int, 4> | true | 아니오 | 스와이프 시작점. 값은 `Click`.`target`과 같다 | - |
| `begin_offset` | array<int, 4> | [0, 0, 0, 0] | 아니오 | `begin`을 기준으로 네 값을 각각 더해 이동시킨 값을 시작점으로 사용 | - |
| `end` | true \| string \| array<int, 2> \| array<int, 4> \| list<true \| string \| array<int, 2> \| array<int, 4>> | true | 아니오 | 스와이프 종점. list는 경유점 추가용이며 end 사이에서 손을 떼지 않는 한 번의 꺾은선 스와이프 | list 지원 v4.5.x |
| `end_offset` | array<int, 4> \| list<array<int, 4>> | [0, 0, 0, 0] | 아니오 | `end`를 기준으로 네 값을 각각 더해 이동시킨 값을 종점으로 사용 | - |
| `duration` | uint \| list<uint> | 200 | 아니오 | 스와이프 지속 시간(ms) | - |
| `end_hold` | uint \| list<uint> | 0 | 아니오 | 종점 도착 후 손을 떼기 전 추가 대기 시간(ms) | - |
| `only_hover` | bool | false | 아니오 | 마우스 호버 이동만 수행하며 누르기/떼기 없음 | - |

### `MultiSwipe`

멀티 핑거 직선 스와이프이다.

- 공통 필드 사용: `contact`, `pressure` (`swipes` 요소 안에서)
- 주의: `swipes` 요소의 `contact` 기본값은 0이 아니라 해당 스와이프의 배열 내 인덱스(0부터)이다.
- 주의: 배열 요소의 순서는 영향이 없으며 `starting`만을 기준으로 순서를 정한다.
- 예시: [원본](PipelineProtocol.md#multiswipe)

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `swipes` | list<object> | - | 예 | 여러 스와이프의 배열 | - |
| `swipes[].starting` | uint | 0 | 아니오 | 이 action 안에서 `starting` ms가 되었을 때 해당 스와이프를 시작 | - |
| `swipes[].begin` | true \| string \| array<int, 2> \| array<int, 4> | true | 아니오 | `Swipe`.`begin`과 같다 | - |
| `swipes[].begin_offset` | array<int, 4> | [0, 0, 0, 0] | 아니오 | `Swipe`.`begin_offset`과 같다 | - |
| `swipes[].end` | true \| string \| array<int, 2> \| array<int, 4> \| list<...> | true | 아니오 | `Swipe`.`end`와 같다(list 경유점 지원) | list 지원 v4.5.x |
| `swipes[].end_offset` | array<int, 4> \| list<array<int, 4>> | [0, 0, 0, 0] | 아니오 | `Swipe`.`end_offset`과 같다 | - |
| `swipes[].duration` | uint \| list<uint> | 200 | 아니오 | 스와이프 지속 시간(ms) | - |
| `swipes[].end_hold` | uint \| list<uint> | 0 | 아니오 | 종점 도착 후 추가 대기 시간(ms) | - |
| `swipes[].only_hover` | bool | false | 아니오 | 호버 이동만 수행 | - |
| `swipes[].contact` | uint | 배열 내 인덱스 | 아니오 | 접점 번호 | v5.0 |
| `swipes[].pressure` | int | 1 | 아니오 | 접점 압력 | v5.0 |

### `TouchDown`

터치 포인트를 누른다. (v5.0)

- 쓰는 곳: `TouchMove`, `TouchUp`과 조합하는 사용자 정의 터치.
- 공통 필드 사용: `contact`, `target`, `target_offset`, `pressure`
- 주의: `pressure` 기본값은 0이며 범위는 컨트롤러 구현에 따라 다르다(공통 필드의 기본값 1과 다름).

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `auto_up` | bool | false | 아니오 | 태스크 중지·종료 또는 컨트롤러 소멸 시 아직 눌린 터치 포인트를 자동으로 뗀다. 대응하는 `TouchUp`이 이미 실행되었다면 다시 떼지 않는다 | v5.10 |

### `TouchMove`

터치 포인트를 이동한다. (v5.0)

- 공통 필드 사용: `contact`, `target`, `target_offset`, `pressure`
- 고유 필드: 없음. 필드의 의미는 `TouchDown`과 같고(`auto_up`은 `TouchDown`에만 적용) 터치 포인트의 위치를 갱신한다.

### `TouchUp`

터치 포인트를 뗀다. (v5.0)

- 공통 필드 사용: `contact`
- 고유 필드: 없음

### `Scroll`

마우스 휠 스크롤이다. (v5.1)

- 공통 필드 사용: `target`(v5.5, 마우스가 먼저 해당 위치로 이동한 뒤 스크롤), `target_offset`(v5.5)
- 주의: Win32 및 macOS 컨트롤러, 그리고 `scroll`을 구현한 커스텀 컨트롤러가 지원한다.
- 주의: `dx`/`dy`는 스크롤 증분으로 그대로 전송된다. Windows 표준 휠 한 칸은 120(WHEEL_DELTA)이므로 120의 정수배를 권장한다.

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `dx` | int | 0 | 아니오 | 수평 스크롤 거리. 양수는 오른쪽, 음수는 왼쪽 | - |
| `dy` | int | 0 | 아니오 | 수직 스크롤 거리. 양수는 위쪽, 음수는 아래쪽 | - |

### `ClickKey`

키를 한 번 누른다.

- 주의: 해당 컨트롤러의 가상 키 코드만 지원한다 (Adb: Android KeyEvent, Win32: Virtual-Key Codes, MacOS: HIToolbox Events.h, WlRoots: linux input-event-codes.h). 링크는 [원본](PipelineProtocol.md#clickkey)을 따른다.
- 주의: PlayCover 컨트롤러는 키 조작을 지원하지 않는다.

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `key` | int \| list<int> | - | 예 | 누를 키(가상 키 코드) | - |

### `LongPressKey`

키를 길게 누른다.

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `key` | int \| list<int> | - | 예 | 누를 키(가상 키 코드) | - |
| `duration` | uint | 1000 | 아니오 | 길게 누르는 지속 시간(ms) | - |

### `KeyDown`

키를 누르되 곧바로 떼지는 않는다. (v5.0)

- 쓰는 곳: `KeyUp`과 함께 사용자 정의 키 타이밍을 구현한다.

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `key` | int | - | 예 | 누를 키(가상 키 코드) | - |
| `auto_up` | bool | false | 아니오 | 태스크 중지·종료 또는 컨트롤러 소멸 시 아직 눌린 키를 자동으로 뗀다. 대응하는 `KeyUp`이 이미 실행되었다면 다시 떼지 않는다 | v5.10 |

### `KeyUp`

키를 뗀다. (v5.0)

- 쓰는 곳: `KeyDown`으로 만든 키 상태를 끝낸다.

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `key` | int | - | 예 | 뗄 키(가상 키 코드) | - |

### `InputText`

텍스트를 입력한다.

- 주의: PlayCover 컨트롤러는 텍스트 입력을 지원하지 않는다.

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `input_text` | string | - | 예 | 입력할 텍스트. 일부 컨트롤러는 ascii만 지원 | - |

### `StartApp`

App을 실행한다.

- 주의: PlayCover 컨트롤러는 앱 실행을 지원하지 않으므로 PlayCover에서 수동으로 실행해야 한다.

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `package` | string | - | 예 | 실행 진입점. package name 또는 activity (예: `com.hypergryph.arknights`, `com.hypergryph.arknights/com.u8.sdk.U8UnityContext`) | - |

### `StopApp`

App을 종료한다.

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `package` | string | - | 예 | 종료할 프로그램의 package name (예: `com.hypergryph.arknights`) | - |

### `StopTask`

현재 태스크 체인(`MaaTaskerPostTask`에 전달된 하나의 태스크 체인)을 중지하고 이후의 인식 루프를 중단한다.

- 필드: 없음

### `Command`

명령을 실행한다.

- 주의: `{IMAGE}` 파일은 프로세스가 종료되기 전에 삭제되므로 영구 보관하려면 직접 복사해야 한다.
- 예시와 실제 실행 명령: [원본](PipelineProtocol.md#command)

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `exec` | string | - | 예 | 실행할 프로그램 경로 | - |
| `args` | list<string> | - | 아니오 | 실행 인자. 치환 지원: `{ENTRY}`(태스크 진입점 이름), `{NODE}`(현재 노드 이름), `{IMAGE}`(스크린샷 저장 파일 경로), `{BOX}`(인식 적중 대상 `[x, y, w, h]`), `{RESOURCE_DIR}`(마지막으로 로드한 리소스 폴더), `{LIBRARY_DIR}`(MaaFW 라이브러리 폴더) | - |
| `detach` | bool | false | 아니오 | 자식 프로세스를 분리해 완료를 기다리지 않고 다음 작업을 계속 실행 | - |

### `Shell`

ADB 기기에서 shell 명령을 실행한다. (v5.3)

- 주의: ADB 컨트롤러에서만 유효하다. 명령 출력은 `MaaTaskerGetActionDetail`을 통해 동작 상세 정보에서 가져온다.

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `cmd` | string | - | 예 | 실행할 shell 명령 (예: `getprop ro.build.version.sdk`) | - |
| `shell_timeout` | int | 20000 | 아니오 | 명령 실행 타임아웃(ms). -1이면 무한 대기 | v5.8 |

### `Screencap`

현재 스크린샷을 `log_dir/screencap/` 디렉터리 아래에 파일로 저장한다.

- 주의: 파일 경로는 `MaaTaskerGetActionDetail`의 동작 상세 정보 `filepath` 필드에서 가져온다.
- 주의: `png`는 항상 무손실이라 `quality`가 무효이다.

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `filename` | string | `타임스탬프_노드이름` | 아니오 | 저장할 파일 이름(확장자 제외) | - |
| `format` | string | `"png"` | 아니오 | 이미지 형식: `"png"` \| `"jpg"` \| `"jpeg"` | - |
| `quality` | int | 100 | 아니오 | 이미지 품질(0-100). `jpg`/`jpeg`에서만 유효 | - |

### `Custom`

`MaaResourceRegisterCustomAction` 인터페이스로 전달된 동작 핸들을 실행한다. ([원본](PipelineProtocol.md#custom-1))

- 공통 필드 사용: `target`(`MaaCustomActionCallback`.`box`로 전달), `target_offset`

| 필드 | 타입 | 기본값 | 필수 | 설명 | 버전 |
| --- | --- | --- | --- | --- | --- |
| `custom_action` | string | - | 예 | 동작 이름. 등록 인터페이스에 전달한 이름과 같고 `MaaCustomActionCallback`.`custom_action_name`으로도 전달된다 | - |
| `custom_action_param` | any | `null` | 아니오 | 동작 매개변수. `MaaCustomActionCallback`.`custom_action_param`으로 전달된다 | - |

## 노드 속성

**v5.1** 노드 속성(Node Attributes)은 `next`와 `on_error` 목록에서 각 노드에 추가 동작 제어 매개변수를 지정한다. 기본 구문은 노드 이름만 담는 목록(`"next": ["B", "C", "D"]`)이다. [원본](PipelineProtocol.md#기본-구문)

### 속성 설정 방식

두 형식은 기능이 동등하며, 배열 안에서 섞어 쓸 수 있다(이종 배열).

| 형식 | 구문 | 예시 | 설명 |
| --- | --- | --- | --- |
| 객체 형식(Object Form) | `NodeAttr` 객체로 `name`과 속성을 명시 | `{"name": "C", "jump_back": true}` | 노드 이름과 속성을 명시적으로 지정 |
| 접두사 형식(Prefix Form) | 노드 이름 앞 대괄호 접두사 | `"[JumpBack]C"` | 대괄호 접두사로 속성을 직접 지정 |

[원본](PipelineProtocol.md#속성-설정-방식)

### 사용 가능한 속성

| 속성 (객체 / 접두사) | 타입 | 기본값 | 용도 | 쓰는 곳 | 지정 방식 | 동작 규칙 | 주의 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `jump_back` / `[JumpBack]` | boolean | `false` | 복귀 메커니즘 활성화. 네트워크 끊김 알림창, 권한 요청 팝업 등 일시적 화면 처리 후 원래 흐름 계속 | `next`, `on_error` 목록의 노드 | `{"name": "D", "jump_back": true}` / `"[JumpBack]D"` | 노드가 인식에 적중하면 그 노드와 후속 노드 체인을 실행하고, 끝나면 부모 노드로 돌아가 부모의 `next` 목록을 처음부터 다시 인식 | 현재 흐름이 오류 처리 경로(`on_error`)에 있으면 복귀하지 않음 |
| `anchor` / `[Anchor]` | boolean | `false` | 앵커 참조 활성화. 노드를 동적으로 참조(마지막으로 처리한 노드로 복귀 등) | `next`, `on_error` 목록의 노드 | `{"name": "X", "anchor": true}` / `"[Anchor]X"` | `name`을 노드 이름이 아닌 앵커 이름으로 간주하며, 런타임에 해당 앵커를 마지막으로 설정한 노드로 해석 | 앵커가 없거나 이미 해제되었으면 해당 후보 노드는 건너뜀 |

`jump_back` 실행 흐름: ① 부모 노드가 `next`를 순서대로 인식 → ② 속성 노드가 적중하면 그 노드와 후속 체인 실행 → ③ 체인 종료 후(오류 처리 경로가 아니면) 부모로 복귀 → ④ 부모가 `next` 처음부터 재인식. [원본](PipelineProtocol.md#jump_back--jumpback)

`anchor` 설정 방법: 노드의 `anchor` 필드로 앵커 이름을 먼저 설정한 뒤, `next`/`on_error`에서 `[Anchor]`/`anchor`로 참조한다. 같은 이름을 다시 설정하면 이전 설정을 덮어쓴다(마지막 설정 노드로 이동).

`anchor` 필드(설정 쪽) 값 형식:

| 형식 | 예시 | 동작 |
| --- | --- | --- |
| 문자열 | `"anchor": "X"` | 앵커 X를 현재 노드로 설정 |
| 객체 | `"anchor": {"X": "TargetNode"}` | 앵커 X를 지정한 노드로 설정(여러 앵커 동시 설정 가능) |
| 객체, 빈 문자열 값 | `"anchor": {"Y": ""}` | 앵커 Y 해제 |

고급 사용(대상 노드 지정·해제)은 pipeline에 변수 메커니즘을 도입하는 것과 비슷하다. [원본](PipelineProtocol.md#anchor--anchor)

향후 더 많은 노드 속성이 제공될 예정이다.

## 결과 정렬 방식

`order_by` 필드로 정렬 방식을 지정하고 `index` 필드와 결합해 특정 결과를 선택한다.

| 방식 | 기준 | 쓰는 곳 | 버전 |
| --- | --- | --- | --- |
| `Horizontal` | x 좌표 오름차순, 같으면 y 오름차순(왼쪽→오른쪽, 위→아래) | 제한 명시 없음 | - |
| `Vertical` | y 좌표 오름차순, 같으면 x 오름차순(위→아래, 왼쪽→오른쪽) | 제한 명시 없음 | - |
| `Score` | 매칭 점수 내림차순. 신뢰도 가장 높은 결과 우선 선택 | 제한 명시 없음 | - |
| `Area` | 인식 박스 면적 내림차순 | `FeatureMatch`, `ColorMatch`, `OCR`, `NeuralNetworkDetect` | - |
| `Length` | 인식된 텍스트 길이, 긴 텍스트가 앞 | `OCR`만 | - |
| `Random` | 결과 순서를 무작위로 섞음. 무작위 선택이 필요한 경우 | 제한 명시 없음 | - |
| `Expected` | `expected` 필드에 지정된 순서. `OCR`은 `expected` 정규식 목록 순서(먼저 매칭된 정규식의 결과가 앞), `NeuralNetworkClassify`/`NeuralNetworkDetect`는 `expected` 분류 인덱스 목록 순서. 어떤 expected에도 매칭되지 않은 결과는 맨 뒤 | `OCR`, `NeuralNetworkClassify`, `NeuralNetworkDetect` | v5.1 |

`Horizontal` 배치(1~8 순서): `| 1 3 5 7 | / | 2 4 6 8 |`, `Vertical` 배치: `| 1 2 3 4 | / | 5 6 7 8 |`. [원본](PipelineProtocol.md#horizontal)

## 화면 정지 대기

일정 시간 연속으로 화면에 큰 변화가 없어야 동작으로 넘어간다. 필드 값(`pre_wait_freezes`, `post_wait_freezes`)은 uint 또는 object이며, uint는 `time`과 같은 의미의 간단 지정이다. object이면 다음 필드를 설정할 수 있다.

| 필드 | 타입 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `time` | uint | 1 | 연속 `time` 밀리초 동안 큰 변화가 없어야 동작으로 넘어감 |
| `target` | true \| string \| array<int, 2> \| array<int, 4> | true | 대기 대상 위치. 값은 `Click`.`target`과 같음 |
| `target_offset` | array<int, 4> | [0, 0, 0, 0] | `target` 기준 추가 이동값, 네 값을 각각 더함 |
| `threshold` | double | 0.95 | "큰 변화 없음" 판단용 템플릿 매칭 임계값 |
| `method` | int | 5 | "큰 변화 없음" 판단용 템플릿 매칭 알고리즘(cv::TemplateMatchModes), `TemplateMatch`.`method`와 같음 |
| `rate_limit` | uint | 1000 | 인식 속도 제한(ms). 매 인식은 최소 `rate_limit`ms를 소비하며 부족분은 sleep |
| `timeout` | int | 20 * 1000 | 인식 타임아웃(ms). -1이면 무한 대기 |

주의: 대기 대상은 질감, 문자 등 디테일이 있는 위치를 선택해야 한다. 분산이 낮은 영역(단색, 넓은 그라데이션)은 템플릿 매칭 점수에 변별력이 없어, `method` 5는 노이즈 때문에 "정지"로 판정하지 못하고 `method` 1 / 3은 작은 변화에도 "정지"로 판정한다. [원본](PipelineProtocol.md#화면-정지-대기)

## 노드 알림

노드 알림은 상위 계층의 구현에 의존하며 MaaFramework가 기본 지원하는 기능이 아니다. 지원 여부는 사용 중인 범용 UI의 문서 또는 코드를 참고한다.

| 필드 | 타입 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `focus` | (원본에 명시 없음) | (원본에 명시 없음) | 노드 실행의 특정 단계에서 UI가 사용자에게 사용자 정의 메시지를 표시하도록 설정. [PI 프로토콜](https://github.com/MaaXYZ/MaaFramework/blob/v5.14.3/docs/zh_cn/3.3-ProjectInterfaceV2协议.md#消息模板机制) 참고 |

[원본](PipelineProtocol.md#노드-알림)

