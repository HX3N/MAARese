# guide/l0-11/2a_build_elect
trigger: STORY_FINISH_OR_PAGE_LOADED obt/guide/l0-11/1d_slot_clean|home

1. [클로저] 이제 어느 정도 정리가 끝났네. 그럼 바로 시설을 건설해 볼까?
2. [클로저] 모든 시설에는 전기가 필요하니까, 먼저 발전소를 짓자.
3. [클로저] 정리가 끝난 방을 터치해 봐. — anim=Click, target=broom_tutorial_btn, signal=building_architecture_view_setup
4. [클로저] 확인 버튼을 터치해서 발전소를 지어 줘. — anim=Click, target=btn_build_confirm, signal=building_room_build_confirmed
