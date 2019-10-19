/** @jsx jsx */
import { jsx } from '@emotion/core';
import { MinimalBase } from '../Base';
import { gql } from 'apollo-boost';
import { useQuery } from '@apollo/react-hooks';
import { Loading } from '../components/Loading';
import { objectTypeSpreadProperty } from '@babel/types';

const imageStyle = {
  borderRadius: "12px"
};

const QUERY = gql`
query myQuery{
  users{
    firstName
    lastName
    portfolio{
      stockmodelSet{
        symbol
        quantity
      }
    }
  }
  stocks{
    symbol
    quantity
  }
}`;

export function Index() {
  let contents;

  const { loading, error, data } = useQuery(QUERY);

  if (loading) {
    contents = <Loading></Loading>;
  }
  else if (error) {
    contents = <p>{error}</p>;
  } else {
    console.log(data);
    const { users, stocks } = data;
    contents = (
      <div>
        <p>Number of users: {users.length}</p>
        <p>Number of stocks: {stocks.length}</p>
        <table>
          <tr>
            <th>Name</th>
            <th>Stocks</th>
          </tr>
          {
            users.map((user: any, index: number) =>
              <tr>
                <td>{user.firstName} {user.lastName}</td>
                <td>{user.portfolio.stockmodelSet.length}</td>
              </tr>
            )
          }
        </table>
      </div>
    );
  }

  return <MinimalBase>{contents}</MinimalBase>
}