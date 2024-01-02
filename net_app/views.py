from django.shortcuts import render, redirect
from .forms import CoreTempForm, IntDescriptionForm
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_config, netmiko_send_command
from nornir_utils.plugins.functions import print_result
from nornir_jinja2.plugins.tasks import template_file
import yaml, re
# Create your views here.

cores_dict = [
	{
	"core01":
        {
		"hostname": "10.0.0.254",
		"groups": ["lab_group"]
        },
	"data": {
			"mgmt_ip": "10.32.40.131",
			"site_id": "DCD",
			"switch_num": "1",
			"mgmt_mask": "24",
			"mgmt_gw": "10.32.112.254",
			"tacacs_key": "nc;eikzm882ml#czPs1uu",
			"telecom_space": "B",
			"vpc_peer_src_ip": "10.188.120.0",
			"vpc_peer_dest_ip": "10.188.120.1",
			"logging_srvr": "172.20.5.5"
	}

	},
	{
		"core02":
			{
				"hostname": "192.168.1.58",
				"groups": ["lab_group"]
			},
		"data": {
			"mgmt_ip": "10.32.40.132",
			"site_id": "DCD",
			"switch_num": "2",
			"mgmt_mask": "24",
			"mgmt_gw": "10.32.112.254",
			"tacacs_key": "nc;eikzm882ml#czPs1uu",
			"telecom_space": "B",
			"vpc_peer_src_ip": "10.188.120.1",
			"vpc_peer_dest_ip": "10.188.120.0",
			"logging_srvr": "172.20.5.5"
		}

	},
]


def get_ints(task):
    sh_run_result = task.run(task=netmiko_send_command, command_string="show run | in interface")
    sh_run_result = sh_run_result.result
    interface_obj = sh_run_result.splitlines()
    config_set = []
    for ethint in interface_obj:

        int2 = ethint.strip("interface ")

        # search_string = net_connect.send_command('show cdp neighbors {} detail'.format(int2))

        search_string = task.run(task=netmiko_send_command, command_string="show cdp neighbors {} detail".format(int2))
        match = re.search('Capabilities: Router|Switch', search_string.result)
        if match:
            des_host = re.search(r'usHBC\w+-\w+-\d+', search_string.result)
            des_host_mod = des_host.group()
            des_int = re.search(r'Port ID \(outgoing port\): (.*)\n', search_string.result)
            des_int_mod = des_int.group(1)
            if des_host:
                des_string = 'description {} - {}'.format(des_host_mod, des_int_mod)
                config_set.append(ethint)
                config_set.append(des_string)

    task.run(task=netmiko_send_config, config_commands=config_set)


def nex_conf(task):
    template = task.run(task=template_file, template="nx_template.j2", path="C:\\Users\\marvin.thomas\\PycharmProjects\\nornir_labbing\\net_automation\\net_app\\jinja_templates")
    task.host["stage_conf"] = template.result
    rendered = task.host["stage_conf"]
    configuration = rendered
    with open(f"{task.host}_conf.txt", "w") as f:
        f.write(configuration)

    task.run(task=netmiko_send_config, read_timeout=90, config_file=f"{task.host}_conf.txt")


def core_ip(subnet):
    ip_add = subnet
    split_ip = ip_add.split(".")
    split_ip[3] = "31"
    core1_ip = ".".join(split_ip)
    split_ip[3] = "32"
    core2_ip = ".".join(split_ip)
    split_ip[3] = "254"
    core_gw = ".".join(split_ip)
    return [core1_ip, core2_ip, core_gw]


def index(request):
    return render(request, "net_app/index.html")


def core_temp(request):
    if request.method == 'POST':
        '''
        form = CoreTempForm(request.POST)

        if form.is_valid():
            print(form.cleaned_data)

            cor_ips = core_ip(form.cleaned_data['mgmt_subnet'])
            cores_dict[0]["data"]["mgmt_ip"] = cor_ips[0]
            cores_dict[1]["data"]["mgmt_ip"] = cor_ips[1]
            cores_dict[0]["data"]["mgmt_gw"] = cor_ips[2]
            cores_dict[1]["data"]["mgmt_gw"] = cor_ips[2]

            with open("./net_app/yaml_files/hosts6.yaml", "w") as f:
                yaml.dump(cores_dict, f)
            '''
        nr = InitNornir(
            config_file="C:\\Users\\marvin.thomas\\PycharmProjects\\nornir_labbing\\net_automation\\net_app\\yaml_files\\config.yaml")
        result = nr.run(task=nex_conf)
        print_result(result)
        return redirect("thank-you")
    else:

        return render(request, "net_app/core_build.html")


def thank_you(request):
    return render(request, "net_app/thanks.html")


def int_descriptions(request):
    if request.method == 'POST':
        nr = InitNornir(
            config_file="C:\\Users\\marvin.thomas\\PycharmProjects\\nornir_labbing\\net_automation\\net_app\\yaml_files\\config.yaml")
        result = nr.run(task=get_ints)
        print_result(result)
        return redirect("thank-you")
    else:
        form = IntDescriptionForm()
    return render(request, "net_app/int_description.html", {"form": form})


def ios_up(request):
    if request.method == 'POST':
        nr = InitNornir(
            config_file="C:\\Users\\marvin.thomas\\PycharmProjects\\nornir_labbing\\net_automation\\net_app\\yaml_files\\config.yaml")

