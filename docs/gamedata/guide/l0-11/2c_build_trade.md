# guide/l0-11/2c_build_trade
trigger: STORY_FINISH_OR_PAGE_LOADED obt/guide/l0-11/2b_build_manu|home

1. [클로저] 마지막으로 무역소를 지어보자.
2. [클로저] 무역소는 오더, 다시 말해 주문받은 상품을 정기적으로 납품해서 안정적으로 용문폐를 수급할 수 있는 곳이야! 이 시설의 랭크가 오르면 합성옥 오더도 받을 수 있게 되지.
3. [클로저] 그럼 마지막으로 청소한 방을 터치해 봐. — anim=Click, target=broom_tutorial_btn, signal=building_architecture_view_setup
4. [클로저] 확인 버튼을 터치해서 무역소를 지어 보자. — anim=Click, target=btn_build_confirm, signal=building_room_build_confirmed
5. [클로저] 좋아, 이제 기본적인 설비는 다 갖춰졌네.
6. [클로저] 그럼 박사, 이제 설비들을 어떻게 운영하는지 알아야겠지?
7. [클로저] 일반 모드로 전환 부탁해~ — anim=Click, target=archi_switch_hotspot, signal=building_opmode_changed
