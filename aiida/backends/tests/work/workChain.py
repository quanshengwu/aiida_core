# -*- coding: utf-8 -*-

import sys
import inspect

from aiida.backends.testbase import AiidaTestCase
from plum.engine.ticking import TickingEngine
import plum.process_monitor
from aiida.orm.calculation.job.quantumespresso.pw import PwCalculation
from aiida.work.workchain import WorkChain,\
    ToContext, _Block, _If, _While, if_, while_
from aiida.work.workchain import _WorkChainSpec, Outputs
from aiida.work.workfunction import workfunction
from aiida.work.run import async
from aiida.orm.data.base import Int, Str
import aiida.work.util as util

__copyright__ = u"Copyright (c), This file is part of the AiiDA platform. For further information please visit http://www.aiida.net/. All rights reserved."
__license__ = "MIT license, see LICENSE.txt file."
__version__ = "0.7.0"
__authors__ = "The AiiDA team."


PwProcess = PwCalculation.process()


class Wf(WorkChain):
    # Keep track of which steps were completed by the workflow
    finished_steps = {}

    @classmethod
    def define(cls, spec):
        super(Wf, cls).define(spec)
        spec.input("value")
        spec.input("n")
        spec.dynamic_output()
        spec.outline(
            cls.s1,
            if_(cls.isA)(
                cls.s2
            ).elif_(cls.isB)(
                cls.s3
            ).else_(
                cls.s4
            ),
            cls.s5,
            while_(cls.ltN)(
                cls.s6
            ),
        )

    def __init__(self):
        super(Wf, self).__init__()
        # Reset the finished step
        self.finished_steps = {
            k: False for k in
            [self.s1.__name__, self.s2.__name__, self.s3.__name__,
             self.s4.__name__, self.s5.__name__, self.s6.__name__,
             self.isA.__name__, self.isB.__name__, self.ltN.__name__]
        }

    def s1(self):
        self._set_finished(inspect.stack()[0][3])

    def s2(self):
        self._set_finished(inspect.stack()[0][3])

    def s3(self):
        self._set_finished(inspect.stack()[0][3])

    def s4(self):
        self._set_finished(inspect.stack()[0][3])

    def s5(self):
        self._set_finished(inspect.stack()[0][3])

    def s6(self):
        self.ctx.counter = self.ctx.get('counter', 0) + 1
        self._set_finished(inspect.stack()[0][3])

    def isA(self):
        self._set_finished(inspect.stack()[0][3])
        return self.inputs.value.value == 'A'

    def isB(self):
        self._set_finished(inspect.stack()[0][3])
        return self.inputs.value.value == 'B'

    def ltN(self):
        keep_looping = self.ctx.get('counter') < self.inputs.n.value
        if not keep_looping:
            self._set_finished(inspect.stack()[0][3])
        return keep_looping

    def _set_finished(self, function_name):
        self.finished_steps[function_name] = True


class TestContext(AiidaTestCase):
    def test_attributes(self):
        c = WorkChain.Context()
        c.new_attr = 5
        self.assertEqual(c.new_attr, 5)

        del c.new_attr
        with self.assertRaises(AttributeError):
            c.new_attr

    def test_dict(self):
        c = WorkChain.Context()
        c['new_attr'] = 5
        self.assertEqual(c['new_attr'], 5)

        del c['new_attr']
        with self.assertRaises(KeyError):
            c['new_attr']


class TestWorkchain(AiidaTestCase):
    def setUp(self):
        super(TestWorkchain, self).setUp()
        self.assertEquals(len(util.ProcessStack.stack()), 0)
        self.assertEquals(len(plum.process_monitor.MONITOR.get_pids()), 0)

    def tearDown(self):
        super(TestWorkchain, self).tearDown()
        self.assertEquals(len(util.ProcessStack.stack()), 0)
        self.assertEquals(len(plum.process_monitor.MONITOR.get_pids()), 0)

    def test_run(self):
        A = Str('A')
        B = Str('B')
        C = Str('C')
        three = Int(3)

        # Try the if(..) part
        Wf.run(value=A, n=three)
        # Check the steps that should have been run
        for step, finished in Wf.finished_steps.iteritems():
            if step not in ['s3', 's4', 'isB']:
                self.assertTrue(
                    finished, "Step {} was not called by workflow".format(step))

        # Try the elif(..) part
        finished_steps = Wf.run(value=B, n=three)
        # Check the steps that should have been run
        for step, finished in finished_steps.iteritems():
            if step not in ['isA', 's2', 's4']:
                self.assertTrue(
                    finished, "Step {} was not called by workflow".format(step))

        # Try the else... part
        finished_steps = Wf.run(value=C, n=three)
        # Check the steps that should have been run
        for step, finished in finished_steps.iteritems():
            if step not in ['isA', 's2', 'isB', 's3']:
                self.assertTrue(
                    finished, "Step {} was not called by workflow".format(step))

    def test_incorrect_outline(self):
        class Wf(WorkChain):
            @classmethod
            def define(cls, spec):
                super(Wf, cls).define(spec)
                # Try defining an invalid outline
                spec.outline(5)

        with self.assertRaises(ValueError):
            Wf.spec()

    def test_context(self):
        A = Str("a")
        B = Str("b")

        @workfunction
        def a():
            return A

        @workfunction
        def b():
            return B

        class Wf(WorkChain):
            @classmethod
            def define(cls, spec):
                super(Wf, cls).define(spec)
                spec.outline(cls.s1, cls.s2, cls.s3)

            def s1(self):
                fa = async(a)
                fb = async(b)
                return ToContext(r1=Outputs(fa.pid), r2=Outputs(fb.pid))

            def s2(self):
                assert self.ctx.r1['_return'] == A
                assert self.ctx.r2['_return'] == B
                fb = async(b)
                # Try overwriting r1
                return ToContext(r1=Outputs(fb.pid))

            def s3(self):
                assert self.ctx.r1['_return'] == B
                assert self.ctx.r2['_return'] == B

        Wf.run()

    def test_str(self):
        self.assertIsInstance(str(Wf.spec()), basestring)

    def test_malformed_outline(self):
        """
        Test some malformed outlines
        """
        spec = _WorkChainSpec()

        with self.assertRaises(ValueError):
            spec.outline(5)

        with self.assertRaises(ValueError):
            spec.outline(type)

    def test_checkpointing(self):
        A = Str('A')
        B = Str('B')
        C = Str('C')
        three = Int(3)

        # Try the if(..) part
        finished_steps =\
            self._run_with_checkpoints(Wf, inputs={'value': A, 'n': three})
        # Check the steps that should have been run
        for step, finished in finished_steps.iteritems():
            if step not in ['s3', 's4', 'isB']:
                self.assertTrue(
                    finished, "Step {} was not called by workflow".format(step))

        # Try the elif(..) part
        finished_steps =\
            self._run_with_checkpoints(Wf, inputs={'value': B, 'n': three})
        # Check the steps that should have been run
        for step, finished in finished_steps.iteritems():
            if step not in ['isA', 's2', 's4']:
                self.assertTrue(
                    finished, "Step {} was not called by workflow".format(step))

        # Try the else... part
        finished_steps =\
            self._run_with_checkpoints(Wf, inputs={'value': C, 'n': three})
        # Check the steps that should have been run
        for step, finished in finished_steps.iteritems():
            if step not in ['isA', 's2', 'isB', 's3']:
                self.assertTrue(
                    finished, "Step {} was not called by workflow".format(step))

    def _run_with_checkpoints(self, wf_class, inputs=None):
        finished_steps = {}

        te = TickingEngine()
        fut = te.submit(wf_class, inputs)
        while not fut.done():
            pid = fut.pid
            te.tick()
            finished_steps.update(wf_class.finished_steps)
            # if not fut.done():
            #     te.stop(pid)
            #     fut = te.run_from(storage.load_checkpoint(pid))
        te.shutdown()

        return finished_steps
