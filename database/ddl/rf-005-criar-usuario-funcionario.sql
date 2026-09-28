create or replace function public.rf005_criar_usuario_funcionario(
    p_nome text,
    p_email text,
    p_cpf text,
    p_user_role text,
    p_password_hash text
)
returns json
language plpgsql
security definer
as $$
declare
    v_user_id uuid;
    v_pessoa_id uuid;
begin

    if exists (
        select 1
        from public.users
        where lower(email) = lower(p_email)
    ) then
        raise exception 'E-mail já cadastrado.';
    end if;

    if p_cpf is not null and exists (
        select 1
        from public.pessoas
        where cpf = p_cpf
    ) then
        raise exception 'CPF já cadastrado.';
    end if;

    insert into public.users (
        email,
        password_hash,
        user_role,
        ativo
    )
    values (
        lower(p_email),
        p_password_hash,
        p_user_role,
        true
    )
    returning id into v_user_id;

    insert into public.pessoas (
        nome,
        cpf,
        user_id,
        ativo
    )
    values (
        p_nome,
        p_cpf,
        v_user_id,
        true
    )
    returning id into v_pessoa_id;

    return json_build_object(
        'id', v_user_id,
        'pessoa_id', v_pessoa_id,
        'nome', p_nome,
        'email', lower(p_email),
        'role', p_user_role,
        'ativo', true
    );

exception
    when others then
        raise;
end;
$$;