# guide/l0-4/0_upgrade_char
trigger: PAGE_LOADED stage|home

1. [PRTS] 아무리 많은 경험을 쌓았다고 하더라도, 일반 대중의 시선으로 보기에 저희는 특이한 조직으로 보일 것입니다.
2. [아미야] 또한, 리유니온은 감염자만으로 구성된 조직이니… 저희가 그들보다 감염자를 더 이해하고 있다고 하기는 어려울 수도 있겠죠.
3. [아미야] 그러니 지휘관으로서, 박사님께선 앞으로도 오퍼레이터들의 상태에 늘 주의를 기울여 주셔요.
4. [PRTS] 이곳이 오퍼레이터 관리 화면입니다. 오퍼레이터의 관리와 훈련을 진행하실 수 있습니다. — anim=Highlight, target=btn_character_repo
5. [PRTS] 선택한 오퍼레이터에게 과거의 작전기록을 보여주어, 그들에게 전장에서 쌓은 지식을 학습하도록 할 수 있습니다.
6. [PRTS] 박사님께서는 특별한 무기를 다루는 분이 아니니 직접 학습하실 필요는 없겠지만, 지휘관으로서 오퍼레이터들과 함께 작전기록을 봐두실 필요가 있습니다.
7. [PRTS] 터치하시면 오퍼레이터의 상세 화면으로 이동합니다. 우선 해당 오퍼레이터의 레벨 정보를 살펴보겠습니다. — anim=Click, target=pool_btn_char_repo_first_item, signal=character_info_resumed
8. [PRTS] 여기에서 오퍼레이터에게 작전기록을 보여주고 레벨을 상승시키면 오퍼레이터의 능력이 강화됩니다. — anim=Highlight, target=panel_hotspot
9. [PRTS] 앞으로의 작전 성공률을 끌어올리기 위해서라도, 지금 바로 오퍼레이터에게 작전기록을 보여주시길 권장드립니다. — anim=Click, target=panel_hotspot, signal=character_info_lvlup_resumed
10. [PRTS] 작전기록 패널에서 작전기록을 길게 터치하면 여러 개 선택하여 경험치 획득 속도를 향상시킬 수 있습니다. — anim=Highlight, target=panel_exp_hotspot
11. [PRTS] 또는, 레벨 패널을 스크롤하여 레벨을 바로 선택할 수 있으며, PRTS가 필요한 수량의 작전기록을 자동으로 선택합니다. — anim=Highlight, target=panel_wheel_picker
