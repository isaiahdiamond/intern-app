# scripts

## `daily.sh`

The scheduled pull. Runs the whole pipeline in order:

```
fetch → classify → clean → icons → describe → read
```

Run it by hand any time:

```sh
bash scripts/daily.sh
```

It appends to `data/daily.log` and never writes to the terminal, so the log is
the record of what happened and when.

### Why each step can fail without stopping the run

A half-finished run that leaves the board more current than it was is worth
more than an aborted one. Every step reports its own failure and the next one
still runs, so a source that is out of quota or an API that is down costs you
that source, not the whole pull.

The order is deliberate: the free steps happen first. If the LLM budget runs
out, the new listings are already in the database — they just have not had
their titles read yet, and the next run picks them up.

### `MAX_CLEAN`

Caps how many titles are cleaned and how many postings are read per run,
currently 400. Reading a title costs roughly $0.0015, so a capped run is about
$0.60 at worst. Without a cap, a day where a source dumps a few thousand
listings would spend several dollars in one go. A backlog is not lost; it is
cleaned over the following runs.

## The schedule

`launchd` runs `daily.sh` at 07:15 and 19:15. The job lives at:

```
~/Library/LaunchAgents/com.isaiahdiamond.internapp.daily.plist
```

| | |
| --- | --- |
| See it is loaded | `launchctl list \| grep internapp` |
| Run it now | `launchctl start com.isaiahdiamond.internapp.daily` |
| Last exit code | `launchctl list com.isaiahdiamond.internapp.daily \| grep LastExitStatus` |
| Turn it off | `launchctl unload ~/Library/LaunchAgents/com.isaiahdiamond.internapp.daily.plist` |
| Turn it back on | `launchctl load ~/Library/LaunchAgents/com.isaiahdiamond.internapp.daily.plist` |

`launchd` rather than `crontab` because it runs a job it missed while the Mac
was asleep, instead of skipping the day.

### The project cannot live in ~/Desktop

macOS refuses to let a background process read `~/Desktop`, `~/Documents` or
`~/Downloads`. A `launchd` job pointed at a project in one of those folders
fails with:

```
getcwd: cannot access parent directories: Operation not permitted
```

The script is fine — it is the OS declining. The fix is for the project to
live somewhere unprotected, which is why it sits in the home folder rather
than on the Desktop. Granting Full Disk Access to `/bin/bash` would also work
and is a worse trade: it hands every background shell script on the machine
full disk access to fix one job.
