_redfish-client()
{
    local cur prev opts
    COMPREPLY=()
    cfgfile=$HOME/.redfish/inventory
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="--help -h --insecure --debug --inventory -i --debugfile --libdebugfile
    --config -c --version"
    cmds="config manager chassis system"
    confcmds="add del modify show showall"
    ocmds="getinfo"
    # done once as used a lot
    mngrs=`redfish-client config show | tail -n +2`

    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        return 0
    fi

    if [ $COMP_CWORD -eq 1 ]; then
        COMPREPLY=( $(compgen -W "${cmds}" -- ${cur}) )
    elif [ $COMP_CWORD -eq 2 ]; then
        case "${prev}" in
            config)
                COMPREPLY=( $(compgen -W "${confcmds}" -- ${cur}) )
                return 0
                ;;
            *)
                COMPREPLY=( $(compgen -W "${ocmds}" -- ${cur}) )
                return 0
                ;;
        esac

    elif [ $COMP_CWORD -eq 3 ]; then
        if [ "${COMP_WORDS[COMP_CWORD-2]}" = "config" ]; then
            case "${prev}" in
                del|modify)
                    COMPREPLY=( $(compgen -W "${mngrs}" -- ${cur}) )
                    return 0
                    ;;
            esac
        else
            # all other cases are getinfo manager
            case "${prev}" in
                getinfo)
                    COMPREPLY=( $(compgen -W "${mngrs}" -- ${cur}) )
                    return 0
                    ;;
            esac
        fi

    elif [ $COMP_CWORD -eq 4 ]; then
        if [ "${COMP_WORDS[COMP_CWORD-3]}" = "config" ] &&
            [ "${COMP_WORDS[COMP_CWORD-2]}" = "modify" ]; then
                COMPREPLY=( $(compgen -W "manager_name url login password" -- ${cur}) )
                return 0
        fi
    fi
}
complete -F _redfish-client redfish-client
