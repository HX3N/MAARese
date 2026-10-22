# guide/l0-11/3a_station_manu
trigger: STORY_FINISH_OR_PAGE_LOADED obt/guide/l0-11/2c_build_trade|home

1. [클로저] 이제 박사가 할 일은 시설마다 오퍼레이터를 배치하는 거야. 설비만 있어서는 제대로 작동하지 않는 경우가 많거든.
2. [클로저] 제조소는 로도스 아일랜드의 제품 생산과 관련된 중요한 시설이야. 여러 가지 제품을 생산할 수 있어.
3. [클로저] 제조소를 터치해 줘. — anim=Click, target=broom_tutorial_btn, signal=building_mode_changed
4. [클로저] 제조소의 가동 상태는 여기에 표시될 거야. — anim=Highlight, target=panel_manufact
5. [클로저] 터치해서 제조 화면을 열어 봐. — anim=Click, target=panel_manufact, signal=building_manufact_routed
6. [클로저] 여기를 터치해서 오퍼레이터를 배치하자. — anim=Click, target=pool_btn_building_room_station_first_empty_slot, signal=building_stationselect_resumed
7. [클로저] 터치해서 오퍼레이터를 골라 줘. — anim=Click, target=pool_btn_building_stationselect_first_item, signal=building_stationselect_charcard_selected
8. [클로저] 확인 버튼을 터치하면 끝! — anim=Click, target=btn_confirm, signal=building_manufact_routed
9. [PRTS] 오퍼레이터 배치가 끝났습니다. 이제 언제든지 제조가 가능합니다.
