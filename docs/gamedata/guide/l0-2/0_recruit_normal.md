# guide/l0-2/0_recruit_normal
trigger: PAGE_LOADED stage|home

1. [아미야] 박사님, 앞으로 닥칠 더 큰 위협에 맞서기 위해서는 지금보다 훨씬 많은 동료가 필요해요.
2. [PRTS] 저번처럼 헤드헌팅으로 동료를 모집하는 것도 좋은 방법이지만, 자원이 한정되어있는 이상 매번 헤드헌팅으로만 채용을 진행하긴 어렵습니다. 이럴 때 공개모집은 또 하나의 선택지가 될 것입니다.
3. [PRTS] 여기를 터치하여 공개모집 화면으로 이동해 주십시오. — anim=Highlight, target=btn_normal_recruit
4. [PRTS] 모집 공고는 이곳을 터치하여 내보낼 수 있습니다. — anim=Click, target=pool_btn_recruit_first_empty_slot, signal=recruit_buildconfig_resumed
5. [아미야] 모집 공고를 낼 때는 오퍼레이터의 모집 요건을 세 개까지 설정하실 수 있으니, 꼭 기억해 주세요. — anim=Highlight
6. [아미야] 또, 모집 시간을 길게 설정할수록 모집 요건에 부합하는 오퍼레이터를 채용할 확률이 높아져요. — anim=Highlight
7. [아미야] 모집 요건과 모집 시간을 다 정하셨다면, 여기를 터치하여 모집을 시작해볼까요! — anim=Highlight, target=panel_hotspot
