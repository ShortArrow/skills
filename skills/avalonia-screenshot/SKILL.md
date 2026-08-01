---
name: avalonia-screenshot
description: |
  Render an Avalonia window to a PNG without starting the application. RenderTargetBitmap.Render(window) is the core; injecting a design-time ViewModel reproduces any screen state on demand.
  This is what makes an edit-capture-check loop on AXAML practical. Capturing before layout completes yields an empty or malformed image, and controls that own a native handle throw when drawn off-screen.
  Triggers: Avalonia screenshot, check an AXAML layout, design preview, render a window without running the app, Avalonia のスクリーンショット, AXAML の見た目確認, デザインプレビュー, ウィンドウのレイアウト確認
allowed-tools: Bash, Read, Glob, Grep
---

# Avalonia Screenshot

`any-screenshot` decides which method applies. This is the Avalonia
render.

**The application is never started.** A window is placed off-screen,
shown, drawn into a `RenderTargetBitmap` and closed. Nothing has to be
clicked through to reach the screen in question, which makes the state
exact and the loop fast.

## The core

```csharp
var bitmap = new RenderTargetBitmap(new PixelSize(w, h), new Vector(96, 96));
bitmap.Render(window);
using var stream = File.Open(path, FileMode.Create, FileAccess.Write);
bitmap.Save(stream);
```

This is **a real window positioned off-screen**, not the
`Avalonia.Headless` package. The GPU backend and the themes apply exactly
as they do in the running application, so the image matches what a user
would see.

```csharp
window.WindowStartupLocation = WindowStartupLocation.Manual;
window.Position = new PixelPoint(-2000, -2000);
window.Show();
```

All of it runs on `Dispatcher.UIThread`.

## Three ways the image comes out wrong

**Layout has not finished.** Capturing straight after `Show()` gives an
empty or half-arranged image. Wait for `LayoutUpdated`, then let the
dispatcher drain at render priority.

```csharp
await window.WaitForLayoutAsync(TimeSpan.FromSeconds(2));
await Dispatcher.UIThread.InvokeAsync(() => { }, DispatcherPriority.Render);
await Task.Delay(200);
```

Write `WaitForLayoutAsync` as an extension that hooks `LayoutUpdated`
once and races it against a timeout. Capturing anyway when the wait
expires — with a warning — is easier to live with than stalling silently.

**Controls that own a native handle.** Anything creating a native window,
video surfaces in particular, fails when drawn off-screen. Find them
through both trees and swap in a `Border` of the same size.

```csharp
window.GetLogicalDescendants().OfType<NativeVideoView>()
  .Concat(window.GetVisualDescendants().OfType<NativeVideoView>())
  .Distinct()
```

**A window that hangs.** Put a timeout on each capture and skip past the
ones that exceed it, so a single bad window does not take the run down.

## Producing different screen states

Inject a design-time ViewModel as the `DataContext`. Recording against
stopped, online against offline, and so on can then be captured from the
same window without driving the application.

**The order of application matters.**

| What | When | Why |
|---|---|---|
| Replacing `DataContext` | **Before** `Show()` | Applies even for a ViewModel that does not implement `INotifyPropertyChanged` |
| Selecting a tab, and similar | **After** `Show()` | The visual tree does not exist until then |

Reach a tab through `GetVisualDescendants().OfType<TabControl>()`, match
on the header text, and set `SelectedIndex`.

## Wiring it up

Add one console project for capturing and let it reference the
application's views and view models. Listing window construction as
lambdas allows `--only <name>` to narrow what runs.

```
src/screenshot/
├── Program.cs           Avalonia initialisation and argument parsing
├── ScreenshotRunner.cs  the rendering, waiting and saving above
└── ScreenshotTarget.cs  window name → construction lambda
```

Writing output to `docs/screenshots/` inside the repository makes the
difference visible in review.
