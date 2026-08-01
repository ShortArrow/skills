---
name: flaui-screenshot
description: |
  Capture a window or a single element of a running app through FlaUI (UI Automation), and assert on the resulting Bitmap's pixels. Capture.Element copies a screen region, so an occluded window needs SetForeground() first; elements are found by AutomationId, not Avalonia's x:Name. Use when the capture must follow an interaction, or must be one control. Not for a whole idle window (windows-screenshot).
allowed-tools: Bash, Read, Glob, Grep
---

# FlaUI Screenshot

`any-screenshot` decides which method applies. This is the route that
takes hold of an application first.

**Element-level capture is what distinguishes it.** Where
`windows-screenshot` can only take a whole window, this can cut out a
single button or panel — and can act on the application before capturing.

## Capturing

```csharp
window.SetForeground();
using var capture = Capture.Element(window);
Bitmap bitmap = capture.Bitmap;
```

`Capture.Element` **copies a screen region** described by the rectangle
UI Automation reports. Unlike `PrintWindow` in `windows-screenshot`, it
**cannot photograph an occluded window**. `SetForeground()` is required,
and it is worth confirming the window really came forward.

```csharp
window.SetForeground();
WaitUntil(() => window.Properties.IsOffscreen.ValueOrDefault == false, TimeSpan.FromSeconds(2));
```

Opening a child window steals the foreground, so the parent has to be
restored before every capture of it.

## Using the image as an assertion

`capture.Bitmap` is a `System.Drawing.Bitmap`, so its pixels can be read
directly. That turns "did this render" into something a test can decide
without a human looking.

```csharp
// Sample the video region only, and treat any bluish pixel as evidence of
// rendering. The region is narrowed so the window chrome and the status
// table's theme colour are never in frame.
for (int y = top; y < bottom; y += 8)
    for (int x = left; x < right; x += 8)
    {
        Color pixel = bitmap.GetPixel(x, y);
        if (pixel.B > pixel.R + 40 && pixel.B > pixel.G + 30) return true;
    }
```

**Narrowing the region is the point.** Scanning the whole window picks up
frame and accent colours that match the expected hue and reports a false
positive.

## Taking hold of the application

```csharp
var automation = new UIA3Automation();
var process = Process.Start(psi);
var app = Application.Attach(process.Id);
```

`Process.Start` followed by `Attach`, rather than `Application.Launch`,
keeps the environment and working directory under your control.

**Identify windows by `AutomationId`.** Titles collide — a splash screen
often shows nothing but the application name — so a title is not an
identity.

```csharp
foreach (var window in app.GetAllTopLevelWindows(automation))
{
    string? id;
    try { id = window.AutomationId; } catch { continue; }   // required
    if (id == "MainWindowRoot") return window;
}
```

**Reading `AutomationId` can throw.** Some top-level windows — splash
screens, programmatically constructed dialogs — do not provide the
property, and an unguarded enumeration falls over on them.

Where a window cannot be identified on its own, reach it through an
element known to be inside it.

```csharp
window.FindFirstDescendant(cf => cf.ByAutomationId(childId)) is not null
```

## Finding elements

```csharp
window.FindFirstDescendant(cf => cf.ByAutomationId("HomeButton"))?.AsButton();
window.FindFirstDescendant(cf => cf.ByName("Connect"))?.AsButton();
```

**Avalonia's `x:Name` does not surface as the UIA `Name` property.** For
elements without an `AutomationId`, the displayed text is the most stable
key — which really means: set an `AutomationId` on anything you intend to
capture.

When something cannot be found, enumerate and look.

```csharp
foreach (var element in window.FindAllDescendants())
    entries.Add($"{element.ControlType}/{element.AutomationId}/'{element.Name}'");
```

`ControlType`, `AutomationId` and `Name` can each throw on read, so wrap
them individually.

## Wiring it up

Put one fixture in the UI test project and give it the application's
lifecycle.

```csharp
public sealed class AppFixture : IDisposable
{
    public UIA3Automation Automation { get; }
    public Application App { get; private set; }
    public Window MainWindow { get; private set; }
    // launch → attach → wait for MainWindow by AutomationId
    // foreground helper, element helpers, graceful restart
}
```

Keeping exactly one instance alive across tests is the constraint that
shapes it. An application holding a single-instance mutex cannot be
started twice, so any test that needs a fresh start — settings being
saved and restored, for instance — needs "close cleanly, then relaunch"
offered by the fixture rather than a second process.

Letting an environment variable override the executable's location keeps
it working when the layout differs, under a sandbox or on CI.

## Consider Avalonia's own route first

If the target is Avalonia and the application need not be running,
`avalonia-screenshot` is faster and more certain: no foreground juggling,
and the desktop is left undisturbed. FlaUI is for capturing **the result
of acting on a live application**.
