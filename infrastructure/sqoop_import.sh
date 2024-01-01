#!bin/bash

TABLE=$1
DATE=$2

# check arguments
if [-z "${DATE}"]; then
    sqoop import -jt local -fs local -m 1 \
        --connect jdbc:mysql://mysql:3306/Book --username root --password root --table items \
        --where "curdate() > $DATE" \
        --target-dir /tmp/target/book_table/$($DATE '+%Y_%m_%d') \
        --as-parquetfile
else
    sqoop import -jt local -fs local -m 1 \
        --connect jdbc:mysql://mysql:3306/Book --username root --password root --table items \
        --target-dir /tmp/target/book_table/total \
        --as-parquetfile
fi