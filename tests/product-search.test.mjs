import test from 'node:test';
import assert from 'node:assert/strict';
import {setTimeout as wait} from 'node:timers/promises';
import {createProductSearch} from '../public/product-search.js';
test('typing is debounced and short input clears suggestions without a request',async()=>{
 const calls=[],states=[];
 const search=createProductSearch({delay:10,interval:0,fetchResults:async q=>{calls.push(q);return {products:[q],count:1}},onChange:s=>states.push(s)});
 search.search('nu');search.search('nut');search.search('nutella');await wait(25);
 assert.deepEqual(calls,['nutella']);assert.deepEqual(states.at(-1).products,['nutella']);
 search.search('n');await wait(15);assert.equal(calls.length,1);assert.deepEqual(states.at(-1).products,[]);
});
test('late responses cannot replace a newer query and cached matches need no network',async()=>{
 const pending={},states=[];let calls=0;
 const search=createProductSearch({delay:0,interval:0,fetchResults:q=>{calls++;return new Promise(resolve=>pending[q]=resolve)},onChange:s=>states.push(s)});
 search.search('old');await wait(5);search.search('new');await wait(5);
 pending.new({products:['new'],count:1});await wait(0);pending.old({products:['old'],count:1});await wait(0);
 assert.deepEqual(states.at(-1).products,['new']);
 search.search('NEW');assert.equal(calls,2);assert.deepEqual(states.at(-1).products,['new']);
});
test('cancel suppresses responses and errors are visible with a retry possible',async()=>{
 let resolve;const states=[];
 const search=createProductSearch({delay:0,interval:0,fetchResults:()=>new Promise(r=>resolve=r),onChange:s=>states.push(s)});
 search.search('food');await wait(5);search.cancel();resolve({products:['food']});await wait(0);assert.equal(states.length,1);
 const retry=createProductSearch({delay:0,interval:0,fetchResults:async()=>{throw Error('Offline')},onChange:s=>states.push(s)});
 retry.search('food');await wait(5);assert.equal(states.at(-1).error,'Offline');assert.equal(states.at(-1).busy,false);
});
test('throttled searches automatically run the latest query',async()=>{
 const calls=[];const search=createProductSearch({delay:0,interval:35,fetchResults:async q=>{calls.push(q);return {products:[],count:0}},onChange:()=>{}});
 search.search('first');await wait(5);search.search('second');search.search('third');await wait(55);assert.deepEqual(calls,['first','third']);
});
