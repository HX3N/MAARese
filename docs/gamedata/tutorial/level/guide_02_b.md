# tutorial/level/guide_02_b
trigger: 없음

1. (전투) Battle.Pause
2. (전투) Battle.EnsureMinSp(charId=char_102_texas(텍사스), sp=100)
3. [아미야] 텍사스 씨는 많은 양의 무기를 사용하여 주위의 적을 단숨에 제압하는 기술이 특기에요. — anim=Highlight
4. [아미야] 하지만 한 번에 많은 무기를 쓰게 되면, 물론 본인에게도 부담이 가겠죠. 그러니 박사님께서 전투 상황을 지켜보고, 기술을 사용할 정확한 타이밍을 알려주셔야 해요. — anim=Highlight
5. (전투) Battle.UnlockFunction(mask=CHARACTER_INFO)
6. (전투) Battle.UnlockFunction(mask=CHARACTER_MENU)
7. [아미야] 많은 수의 적이 텍사스 씨에게 접근하는 타이밍에 텍사스 씨를 터치하고, 스킬 아이콘을 터치하여 지시를 내려주세요.
8. [아미야] 그리고 텍사스 씨를 터치하면, 텍사스 씨의 데이터를 확인할 수 있어요. — anim=Highlight
9. [아미야] "오퍼레이터들의 능력을 하나 파악하는 것으로, 자신의 생존 시간을 11.45초 더 늘릴 수 있다"고, 교관님께서 말씀하신 적이 있어요. 진짜인지 농담인진 잘 모르겠지만… — anim=Click, signal=char_info
10. [아미야] 저지 가능 수는 오퍼레이터가 멈춰 세울 수 있는 적의 수를 뜻해요. — anim=Highlight
11. [아미야] 철수 아이콘을 터치하면 오퍼레이터를 철수시킬 수 있어요. 철수하게 된 오퍼레이터는 일정 시간이 지나면 다시 배치할 수 있게 되고요. — anim=Highlight, target=btn_withdraw
12. [아미야] 오퍼레이터를 박사님께서 직접 철수시키면 배치할 때 쓰는 코스트를 일부 돌려받을 수 있지만, 적에게 쓰러져서 강제 철수 당하는 경우에는 코스트를 돌려받지 못하니, 꼭 오퍼레이터가 쓰러지기 전에 철수 지시를 내려줄 수 있도록 주의해주세요. — anim=Highlight, target=btn_withdraw
13. [아미야] 그럼 스킬을 사용해보죠. — anim=Click, target=btn_skill, signal=use_skill
14. (전투) Battle.Pause(pause=false)
15. (전투) Battle.Pause
16. [아미야] 굉장해요!
17. [아미야] 지휘를 할 땐, 지금처럼 적절한 타이밍을 지켜보다 지시를 내려주는 게 가장 중요해요.
18. [아미야] 아직 긴장을 늦추시면 안 돼요. 혹시라도 박사님께서 쓰러지시기라도 한다면, 저희에게 미래는 없으니까요.
