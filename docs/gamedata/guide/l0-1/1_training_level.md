# guide/l0-1/1_training_level
trigger: STORY_FINISH_OR_PAGE_LOADED obt/guide/l0-1/0_mission_main|home

1. [아미야] 박사님. 로도스 아일랜드의 자료 보관소에 도베르만 교관님께서 만드신 튜토리얼 자료를 봐주시겠어요?
2. [아미야] 이 자료들은 작전에 도움이 되는 기본적인 테크닉을 모아 놓은 거니까, 익혀 두면 분명 큰 도움이 될 거예요.
3. [아미야] 도베르만 교관님께선 아직 구출 작전에 참여 중이시니, 직접 가르쳐주시기는 어려울 것 같네요.
4. [아미야] 예전에 블랙스틸에서 오퍼레이터로 일했던 제시카 씨와 진행한 모의 훈련을 보는 건 어떨까요?
5. [아미야] 이곳을 터치하여 작전 화면으로 이동하여 주십시오. — anim=Highlight, target=btn_battle
6. [아미야] 튜토리얼 스테이지는 이성을 소비하지 않아서, 언제든지 몇 번이고 다시 도전하실 수 있어요. — anim=Highlight, target=pool_btn_train_substage#tr_01
7. [아미야] 여기를 터치하여 작전 전의 편성 화면으로 이동해 주세요. — anim=Click, target=btn_start_battle, signal=squadhome_resumed
8. [아미야] 박사님, 튜토리얼 스테이지에서는 따로 팀을 편성할 수 없어서, 정해진 구성원으로만 클리어하셔야 해요. 만약 클리어하기 어려우시다면, 다른 방향으로 전술을 생각해주시는 게 좋을 것 같아요. — anim=Highlight
9. [아미야] 버튼을 터치하여 튜토리얼을 진행해볼까요? — anim=Click, target=hotspot_startbtn, signal=battle_start
