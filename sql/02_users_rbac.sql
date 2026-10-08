do $$
begin
    if not exists (select 1 from pg_type where typname = 'user_role') then
        create type user_role as ENUM('STUDENT','WARDEN', 'TECHNICIAN');
    end if;
end $$;

create table if not exists users(
    id serial primary key,
    full_name varchar(100) not null,
    email varchar(150) not null unique,
    phone varchar(15) not null unique,
    password_hash varchar(255) not null,
    role user_role not null default 'STUDENT',
    registration_number varchar(20) unique,
    room_id int references rooms(id) on delete set null,
    created_at timestamp with time zone default current_timestamp,

    constraint chk_student_reg_no check(
        (role = 'STUDENT' AND registration_number is not null) or
        (role != 'STUDENT')
    )
);