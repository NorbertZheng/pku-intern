"""
Created on 15:35, May. 24th, 2021
Author: fassial
Filename: expr8.py
Description:
    Excitatory chemical connections cannot substitute for GJ in the formation of local active zones.
"""
import numpy as np
import brainpy as bp
from copy import deepcopy
# local dep
import os
import sys
sys.path.append(os.path.join("..", ".."))
import model
import stimulus
import utils

# macro
DIR_ROOT = os.getcwd()
DIR_FIGS = os.path.join(DIR_ROOT, "figs")
if not os.path.exists(DIR_FIGS): os.mkdir(DIR_FIGS)
DIR_OUTPUTS = os.path.join(DIR_ROOT, "outputs")
if not os.path.exists(DIR_OUTPUTS): os.mkdir(DIR_OUTPUTS)
DIR_OUTPUTS_STIM = os.path.join(DIR_OUTPUTS, "stimulus")
if not os.path.exists(DIR_OUTPUTS_STIM): os.mkdir(DIR_OUTPUTS_STIM)
DIR_OUTPUTS_SPIKE = os.path.join(DIR_OUTPUTS, "spike")
if not os.path.exists(DIR_OUTPUTS_SPIKE): os.mkdir(DIR_OUTPUTS_SPIKE)

## default params
# default stim_params
default_stim_params = {
    "normal": stimulus.stim_params(
        name = "normal",
        height = 200,
        width = 1,
        duration = 1000,
        others = {
            "freqs": np.full((200,), 20., dtype = np.float32),
            "noise": 0.,
        }
    ),
}
# default net_params
default_net_params = {
    "neurons" : {
        "size": (200,),
        "V_init": "reset",
    },
    "GJ": {
        "r": 1,
        "p": 0.,
        "weight": .3,
        "conn": model.connector.IndexConnector(),
    },
    "CHEMS": {
        "r": 30,
        "p": 1.,
        "weight": 2.,
        "conn": model.connector.IndexConnector(),
    }
}

def expr(r_g, p_g, g_gap, dt = 0.01):
    print("processing expr(" + str(r_g) + "," + str(p_g) + "," + str(g_gap) + ")...")

    # init seed
    np.random.seed(0)
    # init backend
    bp.backend.set(dt = dt)
    bp.backend.set(backend = "numpy")

    # init expr_curr
    expr_curr = "normal"

    ## prepare expr
    # init net_params
    net_params = deepcopy(default_net_params)
    net_params["GJ"]["r"] = r_g; net_params["GJ"]["p"] = p_g; net_params["GJ"]["weight"] = g_gap; print(net_params)

    # init inputs
    inputs_neurons = []
    # get stimulus
    stim_fname = os.path.join(
        DIR_OUTPUTS_STIM,
        expr_curr + "-" + str(default_stim_params[expr_curr].duration) + ".csv"
    )
    if os.path.exists(stim_fname):
        # load stim
        stim_neurons = np.loadtxt(
            fname = stim_fname,
            delimiter = ","
        )
    else:
        # get stim
        stim_neurons, _ = stimulus.stimulus.get(
            stim_params = default_stim_params[expr_curr]
        ); stim_neurons += .5
        # save stim
        np.savetxt(fname = stim_fname, X = stim_neurons, delimiter = ",")

    ## exec expr
    # inst FSI
    net = model.FSI(net_params = net_params, run_params = {
        "inputs": stim_neurons,
        "dt": dt,
        "duration": default_stim_params[expr_curr].duration,
    })
    # net run
    net.run(report = True)
    # show net.mon
    net_monitors = net.get_monitors()
    net.show(img_fname = os.path.join(DIR_FIGS,
        expr_curr + "-" + str(r_g) + "-" + str(p_g) + "-" + str(g_gap) + ".png"
    ))
    net.save(spike_fname = os.path.join(DIR_OUTPUTS_SPIKE,
        expr_curr + "-" + str(dt) + "-" + str(r_g) + "-" + str(p_g) + "-" + str(g_gap) + ".csv"
    ))

    ## compute omega
    print(net_monitors.spike.T.shape)
    omega = utils.get_omega(
        spike = net_monitors.spike.T,
        bin = 100,
        dt = dt,
        N = 20
    )

    return omega

def main(dt = 0.01):
    # init r_gs & p_gs & g_gaps
    r_gs = [3, 5, 10, 30]
    p_gs = [0., .3, .5, 1.]
    g_gaps = np.arange(0, 1.01, 0.05).astype(dtype = np.float32)

    # exec expr
    for r_g in r_gs:
        # init omegas
        omegas = []
        # set omegas
        for p_g in p_gs:
            omega = []
            for g_gap in g_gaps:
                omega.append(expr(
                    r_g = r_g,
                    p_g = p_g,
                    g_gap = g_gap,
                    dt = dt
                ))
            omegas.append(omega)
        omegas = np.array(omegas, dtype = np.float32)

        # save omegas
        np.savetxt(
            fname = os.path.join(DIR_OUTPUTS, "omegas" + "-" + str(r_g) + ".csv"),
            X = omegas,
            delimiter = ","
        )

if __name__ == "__main__":
    main()

