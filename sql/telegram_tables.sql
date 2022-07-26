create table telegram_users (
	id serial primary key not null,
	chat_id varchar(256) not null,
	status bool not null
);

create table sent_notis (
	id serial primary key not null,
	user_id int references telegram_users (id) not null,
	order_id int references ksfront_sheetdata (id) on delete cascade not null
);

create procedure insert_sent_notis (chatid varchar(256), orderno int)
as $$
begin
	if (select exists (select id from sent_notis))
	then
		insert into sent_notis (id, user_id, order_id) values (
			(select max(id) from sent_notis) + 1,
			(select id from telegram_users where chat_id=chatid),
			(select id from ksfront_sheetdata where order_no=orderno)
		);
	else
		insert into sent_notis (id, user_id, order_id) values (
			1,
			(select id from telegram_users where chat_id=chatid),
			(select id from ksfront_sheetdata where order_no=orderno)
		);
	end if;
end;
$$ language plpgsql;