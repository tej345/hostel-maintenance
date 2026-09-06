SELECT current_database(), current_user, version();

do $$
begin
	if not exists(select 1 from pg_type where typname = 'gender_type') then
		create type gender_type as ENUM('MALE', 'FEMALE');
	end if;
end $$;


create table if not exists blocks(
	id SERIAL primary key,
	block_name VARCHAR(50) not null unique,
	gender gender_type not null,
	total_floors int not null check(total_floors > 0),
	has_ac boolean default true,
	created_at timestamp with time zone default current_timestamp
);

create table if not exists rooms(
	id SERIAL primary key,
	block_id int not null references blocks(id) on delete cascade,
	room_number varchar(10) not null,
	floor_number int not null check(floor_number >= 0),
	room_type varchar(30) not null,
	created_at timestamp with time zone default current_timestamp,
	constraint uq_block_room unique (block_id, room_number)
);

insert into blocks(block_name, gender, total_floors, has_ac) values
('A Block', 'MALE', 17, TRUE),
('B Block', 'FEMALE', 17, TRUE),
('C Block', 'MALE', 17, TRUE),
('D Block', 'MALE', 16, TRUE),
('E Block', 'MALE', 16, TRUE),
('F Block', 'MALE', 17, TRUE);


