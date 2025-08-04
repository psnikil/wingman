export default async function IsInitialised():Promise<boolean>{

    const res = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/is_init`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    const is_init = await res.json();

    return is_init.is_init;
}