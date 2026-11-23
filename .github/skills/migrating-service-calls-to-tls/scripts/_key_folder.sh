# Sourced, never run: the key folder checks, in one copy. _common.sh sources it
# for the toolkit's scripts; make-csr.sh sources it from its own folder, so a
# consumer kit carries it beside make-csr.sh. Needs bash and a die() function.

# Where to put keys instead, said the same way by every refusal.
KEY_FOLDER_HINT="keys belong in a folder only you can write, outside any repository, for example ~/.tls-migration/private/<project>; when your home folder is itself a repository, a folder you own outside it, made with mkdir -m 700 (never a shared folder such as /tmp or /var/tmp)"

# Refuses a folder that sits inside a source tree: a key there is one 'add .'
# away from being committed. Walks up looking for the marks of a repository
# (.git, .svn, .hg) or of a migration run (tls-migration/); runs no git.
# <what> names the argument the folder came from, so the message points at it.
refuse_inside_repo() {   # <existing folder> [<what>, default TLS_PRIVATE_DIR] [<folder asked for>]
  local dir marker what="${2:-TLS_PRIVATE_DIR}" shown="${3:-$1}"
  dir="$(cd "$1" && pwd -P)"
  while [[ "$dir" != "/" && -n "$dir" ]]; do
    for marker in .git .svn .hg tls-migration; do
      if [[ -e "$dir/$marker" ]]; then
        die "$what ($shown) is inside the repository at $dir (found $marker there). Give $what another folder: $KEY_FOLDER_HINT"
      fi
    done
    dir="$(dirname "$dir")"
  done
}

# "<owner uid> <octal mode>" of a folder, of what a link points to. GNU stat
# first (BSD stat -f means something else there). The mode keeps the sticky,
# setuid and setgid digit on both: GNU %a prints 1777, BSD %Mp%Lp prints 1777
# (and 0755 for a plain folder), so macOS and Linux decide alike.
owner_and_mode() {
  stat -c '%u %a' -L "$1" 2>/dev/null || stat -f '%u %Mp%Lp' -L "$1"
}

# Reads owner_and_mode into the caller's owner and perms; refuses what it cannot read.
read_owner_and_mode() {   # <folder>
  read -r owner perms < <(owner_and_mode "$1" 2>/dev/null || true)
  [[ "${owner:-}" =~ ^[0-9]+$ && "${perms:-}" =~ ^[0-7]{3,4}$ ]] \
    || die "cannot read the owner and mode of $1, so it cannot be checked; $KEY_FOLDER_HINT"
}

# An existing key folder must be ours and writable by nobody else: another
# user who can write it can swap a key or a CA under us.
refuse_foreign_dir() {   # <folder> <what>
  local owner perms
  read_owner_and_mode "$1"
  [[ "$owner" == "$(id -u)" ]] || die "$2 ($1) belongs to another user (uid $owner); $KEY_FOLDER_HINT"
  (( (8#$perms & 8#022) == 0 )) || die "$2 ($1) can be written by other users (mode $perms); $KEY_FOLDER_HINT. If it is yours: chmod go-w $1"
}

# A folder about to be created must sit under a parent that nobody else can
# write or rename things in: ours or root's, and writable by its owner only.
# A shared folder such as /tmp (mode 1777) is refused too, as the hint says:
# the sticky bit stops others renaming our folder, not squatting its name first.
refuse_unsafe_parent() {   # <existing parent> <what>
  local owner perms
  read_owner_and_mode "$1"
  if [[ "$owner" != "$(id -u)" && "$owner" != 0 ]]; then
    die "$2 would be created under $1, which belongs to another user (uid $owner); $KEY_FOLDER_HINT"
  fi
  if (( (8#$perms & 8#022) != 0 )); then
    if (( (8#$perms & 8#1000) != 0 )); then
      die "$2 would be created under $1, a shared folder other users can write (mode $perms); $KEY_FOLDER_HINT"
    fi
    die "$2 would be created under $1, which other users can write (mode $perms); $KEY_FOLDER_HINT"
  fi
}

# Every folder that already exists between TLS_PRIVATE_DIR and <folder> must be
# ours and writable by nobody else, not only the two ends.
refuse_foreign_between() {   # <folder> <what>
  local dir
  dir="$(dirname "$1")"
  while [[ "$dir" == "$TLS_PRIVATE_DIR"/* ]]; do
    [[ -d "$dir" ]] && refuse_foreign_dir "$dir" "$2"
    dir="$(dirname "$dir")"
  done
}

# Creates a private folder. A folder that already exists is checked first
# (outside any repository, ours, writable by nobody else) and its mode is
# left alone; so is every existing folder on the way down from TLS_PRIVATE_DIR.
# A folder still to be made is checked through its nearest existing parent,
# before anything is created. <what> names the argument the folder came from.
ensure_private_dir() {   # <folder> [<what>, default TLS_PRIVATE_DIR]
  local dir="$1" what="${2:-TLS_PRIVATE_DIR}" probe
  # A folder below TLS_PRIVATE_DIR is only as safe as TLS_PRIVATE_DIR itself.
  if [[ "$dir" == "$TLS_PRIVATE_DIR"/* && -d "$TLS_PRIVATE_DIR" ]]; then
    refuse_inside_repo "$TLS_PRIVATE_DIR"
    refuse_foreign_dir "$TLS_PRIVATE_DIR" TLS_PRIVATE_DIR
  fi
  if [[ -d "$dir" ]]; then
    refuse_inside_repo "$dir" "$what"
    refuse_foreign_dir "$dir" "$what"
    refuse_foreign_between "$dir" "$what"
    return
  fi
  # Check the nearest existing parent before creating anything.
  probe="$dir"
  while [[ ! -d "$probe" ]]; do probe="$(dirname "$probe")"; done
  refuse_inside_repo "$probe" "$what" "$dir"
  if [[ "$probe" == "$TLS_PRIVATE_DIR"/* ]]; then
    refuse_foreign_dir "$probe" "$what"
    refuse_foreign_between "$probe" "$what"
  else
    refuse_unsafe_parent "$probe" "$what"
  fi
  mkdir -p "$dir"
  chmod 700 "$dir"
}

# Keys for staging and production are made by a person, never by an assistant
# (D8): the script stops unless its input is a terminal and the person types
# the environment's name when asked. A closed or piped input is refused, so a
# command run by an assistant, a pipeline step or a script never gets past it.
# Nothing has been created when this runs.
confirm_environment() {   # <environment> <what is about to be made>
  case "$1" in staging|production) ;; *) return 0 ;; esac
  if [[ ! -t 0 ]]; then
    die "a $1 key is made only by a person at a terminal: input is not a terminal, so nothing was made. An assistant never runs this for $1: it writes the exact command into tls-migration/requests/<name>.md for the owners of the target and pauses that item."
  fi
  local answer=""
  printf '%s\n' "This makes $2 for $1. It is meant to run where the key will live (the target host or the deployment pipeline)." >&2
  printf 'Type the environment name (%s) to go on, anything else stops: ' "$1" >&2
  IFS= read -r answer || answer=""
  answer="${answer%$'\r'}"
  [[ "$answer" == "$1" ]] || die "not confirmed ('$1' was not typed); nothing was made"
}

