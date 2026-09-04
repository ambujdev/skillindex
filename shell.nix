{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    postgresql
    python3Packages.django
    python3Packages.psycopg2
    python3Packages.pillow
  ];

  shellHook = ''
    echo "========================================================"
    echo "  🚀 Starting Skill Index Environment with PostgreSQL    "
    echo "========================================================"

    export PGDATA="$PWD/.pg_data"
    export PGPORT="5434"
    export PGDATABASE="skill_index_db"
    export PGUSER="''${USER:-focus}"
    export PGHOST="127.0.0.1"

    export USE_POSTGRES="1"
    export POSTGRES_DB="$PGDATABASE"
    export POSTGRES_USER="$PGUSER"
    export POSTGRES_HOST="127.0.0.1"
    export POSTGRES_PORT="$PGPORT"

    # Create directory if needed
    mkdir -p "$PGDATA"

    # Initialize PostgreSQL cluster if not initialized
    if [ ! -f "$PGDATA/PG_VERSION" ]; then
      echo "--> Initializing local PostgreSQL cluster..."
      initdb -D "$PGDATA" -U "$PGUSER" --auth=trust > /dev/null
      echo "listen_addresses = '*'" >> "$PGDATA/postgresql.conf"
      echo "unix_socket_directories = '/tmp,$PGDATA'" >> "$PGDATA/postgresql.conf"
      echo "port = $PGPORT" >> "$PGDATA/postgresql.conf"
    fi

    # Clean stale lock file if postgres daemon crashed or process was killed
    if [ -f "$PGDATA/postmaster.pid" ] && ! pg_isready -h 127.0.0.1 -p "$PGPORT" > /dev/null 2>&1; then
      echo "--> Cleaning stale postmaster.pid..."
      rm -f "$PGDATA/postmaster.pid"
    fi

    # Start PostgreSQL daemon if not already running
    if ! pg_isready -h 127.0.0.1 -p "$PGPORT" > /dev/null 2>&1; then
      echo "--> Starting PostgreSQL daemon on 127.0.0.1:$PGPORT..."
      pg_ctl -D "$PGDATA" -o "-h 127.0.0.1 -k /tmp -p $PGPORT" -l "$PGDATA/postgresql.log" start > /dev/null
      sleep 2
    else
      echo "--> PostgreSQL daemon is already running on 127.0.0.1:$PGPORT."
    fi

    # Ensure database exists
    if ! psql -h 127.0.0.1 -p "$PGPORT" -U "$PGUSER" -lqt | cut -d \| -f 1 | grep -qw "$PGDATABASE"; then
      echo "--> Creating database $PGDATABASE..."
      createdb -h 127.0.0.1 -p "$PGPORT" -U "$PGUSER" "$PGDATABASE"
    fi

    # Run Django Migrations and Seed Data
    echo "--> Running Django migrations..."
    python manage.py makemigrations portal --noinput > /dev/null 2>&1 || true
    python manage.py migrate --noinput > /dev/null

    echo "--> Seeding demo data..."
    python manage.py seed_data

    # Setup trap to stop postgres when exiting nix-shell
    cleanup() {
      echo ""
      echo "========================================================"
      echo "  🛑 Exiting nix-shell: Stopping PostgreSQL server...   "
      echo "========================================================"
      pg_ctl -D "$PGDATA" stop -m fast > /dev/null 2>&1 || true
    }
    trap cleanup EXIT

    echo ""
    echo "✅ Skill Index setup complete!"
    echo "🌐 You can start the server with: python manage.py runserver 8000"
    echo "========================================================"
  '';
}
