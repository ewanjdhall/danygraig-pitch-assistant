# Lab 2 worksheet: interaction flow and storyboards

(The 01_lab2_worksheet.md template was still locked on Canvas when I did this, so I've followed the five phases from the lab page instead.)

**Problem from Lab 1:** when you book a pitch through an AI chat assistant, it turns what you type into booking requirements behind the scenes. You can't see what it thinks you need, so it's hard to tell why it picked (or ruled out) a pitch, and you can't fix it if it got something wrong.

Scenario: a booking assistant for Danygraig Holiday Park. The pitch data is made up and Alex and Bella are placeholder names.

## Phase 1: one inference

- **Senses:** what the guest types in the chat (who's coming, vehicle, dates, anything they need), plus what's free and the pitch details from the booking system (max vehicle length, hook-up, whether dogs are allowed).
- **Infers:** the party's pitch requirements, and from those, which free pitch fits.
- **Does:** shows a "here's what I understood" row of chips the guest can tap and change, then recommends one pitch with reasons and two other options. It doesn't book anything itself. The guest has to tap Book and confirm.
- **Channel:** the chat on the park's booking website (messages, tappable chips, and a pitch card with Book / Change buttons).
- **Could be wrong when:** something is ambiguous or not said outright. For example "two of us plus Bella" when Bella is the dog: it counts her as a third person and misses the pet. Other examples are vehicle length with or without an awning, or "near the toilets" vs "somewhere quiet".

## Phase 2: interaction flow

Image: 02_interaction_flow.png

Goal -> senses the chat and what's free -> infers the pitch requirements -> shows the chips and a recommended pitch in the chat -> feedback: Alex sees the chips, the reasons and the price, then books it or edits a chip -> back to the goal.

Editing a chip is how the guest corrects it. The edit goes back in as new input and the assistant re-infers. The assistant only suggests, so nothing gets booked unless the guest taps Book.

## Phase 3: normal storyboard

Image: 03_storyboard_normal.png (6 frames)

1. Alex wants a pitch with hook-up for a 6m campervan, 14-16 Aug, and opens the booking assistant on the park website.
2. Alex types the trip in their own words.
3. The assistant shows what it understood as chips: 14-16 Aug, 2 adults, campervan 6m, hook-up, pets: none. Any of them can be tapped and changed.
4. It recommends Pitch 7 (hardstanding, hook-up, fits up to 8m, free both nights), with 2 other options and Book / Change buttons.
5. Alex checks the chips, taps Book and gets a summary to confirm.
6. The booking is confirmed in the chat, with an email copy and an easy way to change it later.

## Phase 4: failure and recovery

Image: 04_failure_recovery.png

- **Wrong inference:** "two of us plus Bella..." is read as 3 adults and no pets, so it recommends Pitch 3, which is in the no-dogs area.
- **How Alex notices:** the chips say 3 adults and pets: none, and the reason says "quiet, no-dogs area". All of this is on screen before anything is booked.
- **Recovery:** Alex taps "pets: none" and changes it to 1 dog (or just types "Bella's our dog"). The assistant updates the chips, says what changed and why Pitch 3 doesn't work any more, and offers Pitch 12 instead (dog-friendly, with hook-up). Nothing was booked, so there's nothing to cancel.
- **What the system should learn:** if a name might not be a person, ask before recommending anything ("Is Bella coming as a guest or a pet?"). Anything it assumed rather than was told should show in orange. And this kind of message should go into the extraction test set so the fix stays fixed.
- **Guideline:** Amershi et al. (2019), G9 "support efficient correction". One tap on the wrong chip fixes it, without retyping the whole request.

## Phase 5: secondary user

Image: 05_storyboard_secondary_user.png

**Secondary user:** someone on reception taking a phone booking for a regular who'd rather not book online. It's the same task as Phase 3, but the staff member uses the assistant in the admin system on the caller's behalf.

**Question I picked:** is it apparent why the system acted?

**Storyboard:** the caller asks for "same as last year". Staff type shorthand notes. The assistant shows what it understood and which words each bit came from. Staff check the one thing it only assumed (pets) with the caller. It recommends Pitch 9 and can answer "why not Pitch 12?" (it's booked on 22 Aug). Staff explain that on the phone and book it, and the reasons get saved in the booking note.

**What I changed compared to the guest version:**

1. Each chip shows where it came from in the staff notes, e.g. hook-up <- "EHU".
2. Anything it assumed but wasn't told (pets: none) is orange, so staff know what to ask.
3. If the caller asked for a specific pitch, it can say why it didn't pick it ("why not?").
4. The explanation is saved in the booking note.

**Why:** the staff member has to explain the choice to someone who can't see the screen, and regulars often ask for "their" pitch. A guest mostly just needs to see what it understood. Staff need the why (and the why not) so they can answer the caller and stand behind the booking, and so colleagues can answer questions about it later.

Link to my Lab 1 reading: Wilkinson et al. (2021) found "why not" explanations didn't help general chatbot users, so here they only appear when someone asks about a specific pitch.
