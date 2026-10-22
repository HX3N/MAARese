# guide/l0-11/3c_station_trade
trigger: STORY_FINISH_OR_PAGE_LOADED obt/guide/l0-11/3b_op_manu|home

1. [클로저] 무역소는 로도스 아일랜드에서 가공한 제품을 팔아서 용문폐나 합성옥을 획득할 수 있는 시설이야.
2. [클로저] 제조소랑은 다르게, 무역소의 오더는 납품하고 아이템을 획득하기까지 시간이 오래 걸리지 않아. 납품이 끝나면 바로 거래가 끝나거든.
3. [클로저] 하지만 무역소의 오더는 바깥에서 알아서 들어오는 게 아니라, 오퍼레이터에게 영업을 시켜서 직접 수주해 와야 해.
4. [클로저] 여기를 터치해서 오퍼레이터를 배치하자. — anim=Click, target=pool_btn_building_room_station_first_empty_slot, signal=building_stationselect_resumed
5. [클로저] 터치해서 오퍼레이터를 골라 줘. — anim=Click, target=pool_btn_building_stationselect_first_item, signal=building_stationselect_charcard_selected
6. [클로저] 확인 버튼을 터치하면 마무리! — anim=Click, target=btn_confirm, signal=building_trading_routed
7. [클로저] 오퍼레이터를 배치해 놓으면 정기적으로 오더를 수주해 올 거야.
