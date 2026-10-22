# guide/l0-0/3_battle_ui
trigger: STORY_FINISH_OR_PAGE_LOADED obt/guide/l0-0/2_make_squad|home

1. [PRTS] 작전은 아직 끝나지 않았다는 걸 잊지 말아 주십시오. 혹시 어떻게 작전 현장으로 돌아가시는지 잊으셨다면, 제가 알려드리겠습니다.
2. [PRTS] 이곳을 터치하여 작전 화면으로 이동하여 주십시오. — anim=Highlight, target=btn_battle
3. [PRTS] [스토리] 메뉴를 선택하여 주십시오. — anim=Click, target=mix_story_layout, signal=stage_mix_story_zonetype_selected
4. [PRTS] 작전은 여기서부터 시작됩니다…… 박사님께서 깨어나신 후 바로 상대해야 할 적은, 체르노보그 시내를 파괴하고 있는 리유니온입니다. — anim=Click, target=pool_btn_first_zone, signal=stage_mix_story_retro_routed
5. [PRTS] 탭 하여 스토리 바로가기 — anim=Click, target=panel_mix_story_retro_entrance, signal=zone_switched_or_resumed
6. [PRTS] 작전 지점을 선택하여 주십시오. — anim=Click, target=pool_btn_first_zonestage, signal=stagepreview_resumed
7. [PRTS] 여기를 터치하여 작전 전 편성 화면으로 이동할 수 있습니다. — anim=Click, target=btn_start_battle, signal=squadhome_resumed
8. [PRTS] 여기를 터치하여 작전을 개시하여 주십시오. — anim=Click, target=hotspot_startbtn, signal=battle_start
