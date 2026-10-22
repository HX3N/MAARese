# guide/l0-0/2_make_squad
trigger: STORY_FINISH_OR_PAGE_LOADED obt/guide/l0-0/1_recruit_adv|home

1. [아미야] 박사님, 지금 작전에 참여하는 오퍼레이터들만으로는 앞으로 다가올 위협을 모두 견디기 어려울지도 몰라요.
2. [아미야] 새로운 오퍼레이터들을 작전에 참여시켜 보도록 할까요.
3. [아미야] 구체적인 방법은 PRTS가 설명해 줄 거예요.
4. [PRTS] 우선, 편성 화면으로 이동하여 주십시오. — anim=Highlight, target=btn_squad
5. [PRTS] 이쪽을 터치하여 오퍼레이터를 편성할 수 있습니다. — anim=Click, target=pool_btn_squad_first_empty_slot, signal=squadselect_resumed
6. [PRTS] 오퍼레이터를 선택하고, — anim=Click, target=pool_btn_squad_select_first_item, signal=squadselect_charcard_selected
7. [PRTS] 확인 버튼을 터치하여 주십시오. — anim=Click, target=panel_hotspot, signal=squadhome_resumed
8. [PRTS] 오퍼레이터가 팀에 편성되었습니다. 내비게이션 바를 터치하여 주십시오. — anim=Click, target=btn_topmenu_home, signal=topmenu_shown
9. [PRTS] 이곳을 터치하여 메인 화면으로 돌아갑니다. — anim=Click, target=btn_home, signal=squad_saved
