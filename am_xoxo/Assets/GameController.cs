using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class GameController : MonoBehaviour
{
	public int czyjRuch; // 1 - X ;; 0 - 0
	public int ileRuchow;
	public int koniecGry;
	public int uzyjBota;

	public Button[] u_blocks;
	public Text[] u_texts;
	public Text u_info;

	void Start()
	{
		GameSetup(1);
	}

	void GameSetup(int zaczyna) {
		czyjRuch = zaczyna;
		ileRuchow = 0;
		koniecGry = 0;
		uzyjBota = 1;

		for(int i = 0; i < u_blocks.Length; i++) {
			u_blocks[i].interactable = true;
			u_texts[i].text = "?";
		}

		if (zaczyna == 1) {
			u_info.text = "zaczynaj! (ruch X)";
		} else {
			u_info.text = "zaczynaj! (ruch O)";
		}
	}

	void Update()
	{

	}

	public void use_bot() {
		if (uzyjBota == 1) {
			uzyjBota = 0;
		} else {
			uzyjBota = 1;
		}
	}

	public void move(int i) {
		u_blocks[i].interactable = false;
		if (czyjRuch == 1) {
			u_texts[i].text = "X";
			czyjRuch = 0;
			u_info.text = "(ruch O)";
		} else {
			u_texts[i].text = "O";
			czyjRuch = 1;
			u_info.text = "(ruch X)";
		}

		ileRuchow += 1;
		bool is_won = IsGameWonBy(u_texts[i].text);
		Debug.Log(is_won);

		if (is_won) {
			koniecGry = 1;
			u_info.text = "REZULTAT: WYGRAL -> " + u_texts[i].text;
			for(int j = 0; j < u_blocks.Length; j++) {
				u_blocks[j].interactable = true;
			}
		} else if (is_won == false && ileRuchow == 9) {
			koniecGry = 1;
			u_info.text = "REZULTAT: REMIS";
			for(int j = 0; j < u_blocks.Length; j++) {
				u_blocks[j].interactable = true;
			}
		}
	}

	public void press_button(int i) {
		if (koniecGry == 1) {
			if (IsGameWonBy("X")) {
				GameSetup(0);
			} else {
				GameSetup(1);
			}
			return;
		}
		if (u_blocks[i].interactable == false) {
			return;
		}
		move(i);
		if (uzyjBota == 1 && koniecGry == 0) {
			for(int j = 0; j < u_blocks.Length; j++) {
				if (u_blocks[j].interactable == true) {
					move(j);
					break;
				}
			}	
		}
	}

	private bool IsGameWonBy(string side)
	{
		if (u_texts[0].text == side && u_texts[1].text == side && u_texts[2].text == side)
		{
			return true;
		}
		else if (u_texts[3].text == side && u_texts[4].text == side && u_texts[5].text == side)
		{
			return true;
		}
		else if (u_texts[6].text == side && u_texts[7].text == side && u_texts[8].text == side)
		{
			return true;
		}
		else if (u_texts[0].text == side && u_texts[4].text == side && u_texts[8].text == side)
		{
			return true;
		}
		else if (u_texts[2].text == side && u_texts[4].text == side && u_texts[6].text == side)
		{
			return true;
		}
		else if (u_texts[0].text == side && u_texts[3].text == side && u_texts[6].text == side)
		{
			return true;
		}
		else if (u_texts[1].text == side && u_texts[4].text == side && u_texts[7].text == side)
		{
			return true;
		}
		else if (u_texts[2].text == side && u_texts[5].text == side && u_texts[8].text == side)
		{
			return true;
		}

		return false;
	}
}
