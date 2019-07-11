#include "raylib.h"

enum gamestate
{
    WAIT,
    ATTACK,
    DEFEND
}

gamestate UpdateAndDraw(gamestate CurrentGS)
{
    // Update
    gamestate NextGS = CurrentGS;
        
    switch (CurrentGS)
    {
        case gamestate.WAIT:
            // wait for keypress
            NextGS = gamestate.DEFEND;
            break;
        case gamestate.ATTACK:
            // same as defend but no input tracking
            NextGS = gamestate.WAIT;
            break;
        case gamestate.DEFEND:
            // player stays still
            // enemy moves at constant speed from right to player
            // within frame window, check for input while enemy intersects player
            // if input, set flag
            // display "damage", whether normal or double if input successful
            NextGS = gamestate.ATTACK;
            break;
    }
    
    // Draw
    BeginDrawing();
        ClearBackground(RAYWHITE);

        DrawText("This is a test.", 190, 200, 20, MAROON);
    EndDrawing();
    
    return NextGS;
}

int main()
{
    int screenWidth = 800;
    int screenHeight = 450;
    InitWindow(screenWidth, screenHeight, "raylib [core] example - basic window");
    SetTargetFPS(60);
    
    gamestate CurrentGS = gamestate.WAIT;
    int FrameInState = 0;

    // Main game loop
    while (!WindowShouldClose())    // Detect window close button or ESC key
    {
        gamestate NextGS = UpdateAndDraw(CurrentGS, FrameInState);
        FrameInState++;
        if (NextGS != CurrentGS)
        {
            FrameInState = 0;
        }
        CurrentGS = NextGS;
    }
 
    CloseWindow();        // Close window and OpenGL context

    return 0;
}