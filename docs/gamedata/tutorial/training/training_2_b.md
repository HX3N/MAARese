# tutorial/training/training_2_b
trigger: 없음

1. (전투) Battle.LockFunction(mask=SYSTEM_MENU_INTERACT)
2. (전투) Battle.Pause
3. (전투) Battle.UnlockFunction(mask=CHARACTER_INFO)
4. (전투) Battle.UnlockFunction(mask=CHARACTER_MENU)
5. [도베르만] 제시카, 눈치챘나? 레인저는 '뒤에 있는' 공격 범위 바깥의 적은 공격할 수 없다. — anim=Highlight
6. [도베르만] 레인저를 터치하여 정보를 확인해보도록. — anim=Click, signal=char_info
7. [도베르만] 주황색으로 표시된 구역이 레인저의 공격 범위다. 이 공격 범위는 레인저를 배치할 때 지정한 방향에 따라 고정된다. — anim=Highlight
8. [도베르만] 직접 철수시키거나 적에게 쓰러져 강제 철수된 다음 재배치하지 않는 이상은, 배치가 완료된 오퍼레이터의 방향과 공격 범위는 변경할 수 없다. 그러니 오퍼레이터의 배치 방향을 지정할 땐 특히 더 조심하도록. — anim=Highlight
9. [도베르만] 지금 레인저는 자신의 '뒤에 있는' 원석충을 공격할 수 없다. — anim=Highlight
10. [도베르만] 하지만 문제없어. 레인저의 사각지대는 다른 오퍼레이터를 배치해서 지키면 되니까.
11. [도베르만] 비어있는 공간을 터치하여 전장 화면으로 돌아가 보도록 하지. — anim=Click, signal=exit_char_menu
12. [도베르만] 스나이퍼 오퍼레이터 아드나키엘을 이곳에 배치해라. — anim=Drag, signal=put_down
13. [도베르만] 그리고 위쪽으로 드래그하여 아드나키엘이 위를 바라보도록 해라. 오퍼레이터의 방향까지 지정해줘야 배치가 완료되는 거다. — anim=Drag, signal=select_direction
14. (전투) Battle.UnlockFunction(mask=SYSTEM_MENU_INTERACT)
