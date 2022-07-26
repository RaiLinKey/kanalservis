-- drop table sent_notis;
-- drop table telegram_users;
-- drop table spreadsheet_data;
-- insert into telegram_users (chat_id, status) values ('305973653', false)


create table telegram_users (
	id serial primary key not null,
	chat_id varchar(256) not null,
	status bool not null
);

create table sent_notis (
	id serial primary key not null,
	user_id int references telegram_users (id) not null,
	order_id int references ksfront_sheetdata (id) on delete cascade not null
)