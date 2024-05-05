# 312_Group_Project

**Hello, welcome to our project: Team Rocket's Rocket Reddit. 
Link: https://rocketreddit.com
Rocket Reddit is a pokemon themed social media app that features:**
- Account registration
- Account login
- Logout
- Live chatting with other users
- Media uploads
- Time based collection of website currency called "PokeCoins"
- Interaction where users can steal each other's PokeCoins

**For CSE312 Project Part 3, objective 3 we have this additional feature:**
The ability to select a starter Pokemon. Choosing a starter Pokemon gives users an additional way to stand out besides their usernames as these chosen Pokemon are used as profile pictures. Choosing this starter is a fun process where users can click on a button to be brought to a starter pokemon selection pop up. On this colorful popup screen, pokemon are highlighted to show which Pokemon the user is hovering over and then an animation plays when the user selects a specific Pokemon.

**This feature is not a subset of any other requirement for this course because:** 
- The given starter pokemon are not media uploads, but are a grid of selected static Pokemon files shown to a user, different from homework and project objectives. 
  This grid consists of 3 separate columns depending on the types (grass, fire, water) of the Pokemon.
- You click on a button to bring up a pop up, something we haven't done in class.
- Hovering over the starter pokemon sprites, lights them up depending on which one the user has their mouse over.
- Selecting a starter pokemon has an animation where there is a repeating glow around the selection.
- Not selecting a starter Pokemon, defaults the user to a hopping egg (Like they're about to hatch into a Pokemon). This selection is also changeable and logging out  also resets this selection.
- Profile pictures were not required on homework or project objectives

**Testing Procedure for Part 3, Objective 3**

Test 1: Ensure that the popup works for selecting a starter Pokemon.
1. Navigate to https://rocketreddit.com/
2. Click on the text saying "Don't have an account yet? Click here to register!"
3. Register for an account using the following credentials:
   a. First Name: test2
   b. Last Name: dummy2
   c. Email: test2dummy2@gmail.com
   d. Username: test2dummy2
   e. Password: Abcd1234!
   f. Confirm Password: Abcd1234!
4. Click the register button
5. Fill out the username and password fields given in step 3.
6. Click login.
7. Click the "Change Starter Pokemon" button which can be found on the gray navbar. This button is found on the top left next to the logout button once you log in.
8. Verify that a "Select Your Starter" pop up, comes up in the middle of the page.
9. Verify that there are 3 columns reading "Grass", "Fire", and "Water".
10. Verify that under each of the 3 columns are 5 Pokemon sprites each.
11. Hover over "Turtwig", the 3rd option from top-down under the grass column. It looks like a green, grassy turtle.
12. Ensure that the background turns a lighter shade of green
13. Click on Turtwig.
14. Ensure that a yellow glow appears around your selection repeatedly and the background stays the lighter shade.
15. Hover over "Chimchar", the 1st option from top-down under the fire column. It looks like a fire monkey.
16. Ensure that the background turns a lighter shade of red
17. Click on Chimchar.
18. Ensure that a yellow glow appears around your selection repeatedly and the background stays the lighter shade.
19. Ensure that the yellow glow and lighter background around "Turtwig" are no longer present.
20. Hover over "Squirtle", the last option from top-down under the water column. It looks like a blue turtle.
21. Ensure that the background turns a lighter shade of blue
22. Click on Squirtle.
23. Ensure that a yellow glow appears around your selection repeatedly and the background stays the lighter shade.
24. Ensure that the yellow glow and lighter background around "Chimchar" are no longer present.
25. Click on the "x" on the top right of the "Select Your Starter" pop up.
26. Ensure that the pop up is closed.

Test 2: Ensure the selected Pokemon shows up in the chat.
1. Following from the steps after Test 1, navigate to the right side of the page and type "I am a Pokemon now" in the create a post box.
2. Click send.
3. Verify that the chat box on the left now contains your new post with the "Squirtle" sprite next to the username "test2dummy2". You may have to scroll down to see your chat.

Test 3: Ensure that the starter is reset to an egg.
1. Following from the steps after Test 2, click on the logout button at the top left of the screen, on the gray navbar.
2. Fill out the username and password fields given in Test 1, step 3.
3. Click login.
4. Type "Hello World" in the create a post box on the rightside of the screen
5. Click send
6. Find the post you just made on the chat box on the left side of the screen. You may have to scroll down. This chat will have the username "test2dummy2" next to the words "Hello World".
7.  Verify that the "Squirtle" sprite is not next to this post.
8.  Verify that a white, jumping egg with green spots is the sprite showing up next to the post.
