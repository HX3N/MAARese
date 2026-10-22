# tutorial/level/guide_01_d
trigger: 없음

1. (전투) Battle.Pause
2. [아미야] 아 참, 아직 궁금하신 게 분명 많으시겠죠.
3. [아미야] 기본적인 화면 정보를 몇 가지 소개해 드릴게요.
4. (전투) Battle.UnlockFunction(mask=PAUSE_BUTTON)
5. [아미야] 오른쪽 위에 보이는 건 '일시정지' 버튼이에요. 터치하면 작전 진행을 일시정지하거나 계속 진행할 수 있죠. — anim=Highlight
6. (전투) Battle.UnlockFunction(mask=SPEED_SWITCHER_BUTTON)
7. [아미야] 일시정지 버튼 왼쪽에 있는 건 '속도 변경' 버튼이에요. 이 버튼을 눌러 작전의 진행 속도를 조절할 수 있습니다. — anim=Highlight, target=btn_speed_level
8. (전투) Battle.UnlockFunction(mask=BATTLE_STATUS)
9. [아미야] 위에 보이는 건 총 HP에요. 파란색 칸까지 적이 침입했을 때 견뎌낼 수 있는 적의 숫자를 표시해주죠. — anim=Highlight
10. [아미야] 그 옆에 있는 건 적 정보예요. 공격해오는 적의 총 숫자와 이미 쓰러뜨린 적의 숫자를 확인할 수 있어요. — anim=Highlight
11. [아미야] 이 정보들을 익혀두면, 분명 박사님의 지휘에 많은 도움이 될 거예요.
