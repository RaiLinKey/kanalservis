-- select * from telegram_users;
-- select * from sent_notis;
-- select * from ksfront_sheetdata order by id;

-- delete from sent_notis;
-- delete from telegram_users;
-- select t1.chat_id, t3.order_no from telegram_users as t1
-- join sent_notis as t2 on t1.id=t2.user_id
-- join spreadsheet_data as t3 on t3.id=t2.order_id
-- where t1.chat_id = '305973652'
-- call insert_sent_notis ('305973652', 1835607)
-- call insert_sent_notis ('305973652', 1235370)
drop procedure insert_sent_notis (chatid varchar(256), orderno int);

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