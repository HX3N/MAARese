# guide/l0-1/0_mission_main
trigger: PAGE_LOADED stage|home

1. [아미야] 사실, 로도스 아일랜드는 정규적인 사내 업무뿐만 아니라, 외부에서 업무 의뢰를 받는 경우도 있어요.
2. [PRTS] 효율적으로 업무를 처리하기 위해서는, 어떻게 임무를 관리해야 하는지 배우셔야 합니다.
3. [아미야] 박사님, 여기를 터치해서 임무 화면으로 이동해 주세요. — anim=Highlight, target=btn_mission
4. [아미야] 이곳에선 앞으로 해야 하는 임무 목록을 볼 수 있어요.
5. [아미야] 여기서 현재 진행 중인 주요 임무 목록을 확인할 수 있죠. — anim=Highlight, target=tab_hotspot_mainmission
6. [아미야] 여기를 터치해서 이번 임무의 보상을 받아 주세요. — anim=Click, target=hotspot_draw, signal=mission_confirmed_mission
7. (대기) signal=gainitem_routed
8. [아미야] 지금은 비상사태니만큼, 사용할 수 있는 자원은 모두 사용해야겠죠. — anim=Click, target=confirm_button, signal=gainitem_confirmed
9. [PRTS] 다른 임무는 언제든지 본 화면으로 돌아와 확인하실 수 있습니다.
10. [PRTS] 지금은, 짚고 넘어가셔야 할 중요 사항이 하나 더 있습니다.
